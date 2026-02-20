#!/usr/bin/env python3
"""
PropChain — Contract Deployment Script
Deploys all 6 smart contracts in the correct order and saves App IDs to .env
"""

import os
import sys
import time
from pathlib import Path

from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import (
    ApplicationCreateTxn,
    OnComplete,
    StateSchema,
    wait_for_confirmation,
)
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────

ALGOD_SERVER = os.getenv("ALGOD_SERVER", "https://testnet-api.algonode.cloud")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "")
ALGOD_PORT = os.getenv("ALGOD_PORT", "443")
ORACLE_MNEMONIC = os.getenv("ORACLE_MNEMONIC", "")
ENV_FILE = Path(__file__).parent / ".env"

# Contract deployment order: dependencies flow downward
CONTRACTS = [
    {
        "name": "SPVRegistry",
        "env_key": "APP_ID_SPV_REGISTRY",
        "file": "contracts/spv_registry.py",
        "global_schema": StateSchema(num_uints=2, num_byte_slices=1),
        "local_schema": StateSchema(num_uints=0, num_byte_slices=0),
        "deps": [],
    },
    {
        "name": "PropertyRegistry",
        "env_key": "APP_ID_PROPERTY_REGISTRY",
        "file": "contracts/property_registry.py",
        "global_schema": StateSchema(num_uints=2, num_byte_slices=2),
        "local_schema": StateSchema(num_uints=0, num_byte_slices=0),
        "deps": ["APP_ID_SPV_REGISTRY"],
    },
    {
        "name": "FractionalToken",
        "env_key": "APP_ID_FRACTIONAL_TOKEN",
        "file": "contracts/fractional_token.py",
        "global_schema": StateSchema(num_uints=2, num_byte_slices=2),
        "local_schema": StateSchema(num_uints=0, num_byte_slices=0),
        "deps": ["APP_ID_PROPERTY_REGISTRY"],
    },
    {
        "name": "RentDistributor",
        "env_key": "APP_ID_RENT_DISTRIBUTOR",
        "file": "contracts/rent_distributor.py",
        "global_schema": StateSchema(num_uints=2, num_byte_slices=0),
        "local_schema": StateSchema(num_uints=0, num_byte_slices=0),
        "deps": ["APP_ID_PROPERTY_REGISTRY", "APP_ID_FRACTIONAL_TOKEN"],
    },
    {
        "name": "GovernanceVoting",
        "env_key": "APP_ID_GOVERNANCE",
        "file": "contracts/governance_voting.py",
        "global_schema": StateSchema(num_uints=3, num_byte_slices=0),
        "local_schema": StateSchema(num_uints=0, num_byte_slices=0),
        "deps": ["APP_ID_PROPERTY_REGISTRY", "APP_ID_FRACTIONAL_TOKEN"],
    },
    {
        "name": "SettlementEngine",
        "env_key": "APP_ID_SETTLEMENT",
        "file": "contracts/settlement_engine.py",
        "global_schema": StateSchema(num_uints=0, num_byte_slices=1),
        "local_schema": StateSchema(num_uints=0, num_byte_slices=0),
        "deps": [
            "APP_ID_PROPERTY_REGISTRY",
            "APP_ID_FRACTIONAL_TOKEN",
            "APP_ID_GOVERNANCE",
            "APP_ID_SPV_REGISTRY",
        ],
    },
]

EXPLORER_BASE = "https://testnet.algoexplorer.io/application"


def get_algod_client() -> algod.AlgodClient:
    """Create Algorand client connection.
    Algonode public endpoints reject the x-algo-api-token header when blank.
    We override headers to send nothing when no token is configured.
    """
    if ALGOD_TOKEN:
        return algod.AlgodClient(ALGOD_TOKEN, ALGOD_SERVER)
    # No token — pass empty string but clear the default header algosdk sends
    return algod.AlgodClient("", ALGOD_SERVER, headers={"X-Algo-API-Token": ""})


def get_deployer_account() -> tuple[str, str]:
    """Returns (private_key, address) from ORACLE_MNEMONIC."""
    if not ORACLE_MNEMONIC:
        console.print("[red]❌ ORACLE_MNEMONIC not set in .env[/red]")
        sys.exit(1)
    private_key = mnemonic.to_private_key(ORACLE_MNEMONIC)
    address = account.address_from_private_key(private_key)
    return private_key, address


def deploy_contract(
    client: algod.AlgodClient,
    private_key: str,
    sender: str,
    contract: dict,
    deployed_ids: dict,
) -> int:
    """Deploy a single contract and return the App ID."""
    console.print(f"\n[yellow]⏳ Deploying {contract['name']}...[/yellow]")

    # Get suggested params
    sp = client.suggested_params()

    # Build application create transaction
    # NOTE: In production, you'd compile the Puya contract to TEAL first
    # using `algokit compile py <file>`. For now we use a placeholder approval
    # program. Replace with compiled TEAL bytes after running `algokit build`.
    approval_program = b"\x06\x81\x01"  # #pragma version 6; int 1
    clear_program = b"\x06\x81\x01"

    # Build app args from dependency App IDs
    app_args = []
    for dep_key in contract["deps"]:
        dep_id = deployed_ids.get(dep_key, 0)
        app_args.append(dep_id.to_bytes(8, "big"))

    txn = ApplicationCreateTxn(
        sender=sender,
        sp=sp,
        on_complete=OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=contract["global_schema"],
        local_schema=contract["local_schema"],
        app_args=app_args if app_args else None,
    )

    # Sign and submit
    signed_txn = txn.sign(private_key)
    tx_id = client.send_transaction(signed_txn)
    console.print(f"  📤 Submitted: {tx_id}")

    # Wait for confirmation
    result = wait_for_confirmation(client, tx_id, 4)
    app_id = result["application-index"]

    console.print(
        f"  [green]✅ {contract['name']} deployed![/green] App ID: [bold]{app_id}[/bold]"
    )
    console.print(f"  🔗 {EXPLORER_BASE}/{app_id}")

    return app_id


def save_app_id(env_key: str, app_id: int):
    """Save deployed App ID back to .env file."""
    env_path = str(ENV_FILE)
    if ENV_FILE.exists():
        set_key(env_path, env_key, str(app_id))
    else:
        with open(env_path, "a") as f:
            f.write(f"{env_key}={app_id}\n")


def main():
    console.print(
        Panel.fit(
            "[bold cyan]PropChain — Contract Deployment[/bold cyan]\n"
            "Deploying 6 smart contracts to Algorand",
            border_style="cyan",
        )
    )

    # Initialize client and deployer
    client = get_algod_client()
    private_key, address = get_deployer_account()

    # Verify connection
    try:
        status = client.status()
        console.print(
            f"[green]✅ Connected to Algorand[/green] — "
            f"Last round: {status['last-round']}"
        )
    except Exception as e:
        console.print(f"[red]❌ Failed to connect: {e}[/red]")
        sys.exit(1)

    console.print(f"📋 Deployer address: [bold]{address}[/bold]")

    # Check balance
    try:
        info = client.account_info(address)
        balance = info["amount"] / 1_000_000
        console.print(f"💰 Balance: [bold]{balance:.2f} ALGO[/bold]")
        if balance < 10:
            console.print(
                "[red]⚠️  Low balance! Need at least 10 ALGO for deployment.[/red]"
            )
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to check balance: {e}[/red]")
        sys.exit(1)

    # Deploy contracts in sequence
    deployed_ids: dict[str, int] = {}

    for contract in CONTRACTS:
        try:
            app_id = deploy_contract(
                client, private_key, address, contract, deployed_ids
            )
            deployed_ids[contract["env_key"]] = app_id
            save_app_id(contract["env_key"], app_id)
        except Exception as e:
            console.print(
                f"[red]❌ Failed to deploy {contract['name']}: {e}[/red]"
            )
            sys.exit(1)

    # Print summary table
    console.print("\n")
    table = Table(title="🏗️  PropChain Deployment Summary", border_style="cyan")
    table.add_column("Contract", style="bold")
    table.add_column("App ID", style="green")
    table.add_column("Explorer Link", style="dim")

    for contract in CONTRACTS:
        app_id = deployed_ids[contract["env_key"]]
        table.add_row(
            contract["name"],
            str(app_id),
            f"{EXPLORER_BASE}/{app_id}",
        )

    console.print(table)
    console.print(f"\n📋 Creator address: [bold]{address}[/bold]")
    console.print("[green]✅ All App IDs saved to .env[/green]")
    console.print(
        "\n[bold cyan]🚀 PropChain deployment complete![/bold cyan]"
    )


if __name__ == "__main__":
    main()
