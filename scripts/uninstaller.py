#!/usr/bin/env python3
"""
Galaxy Repository Uninstaller

Uninstalls repositories from a Galaxy instance using BioBlend.
"""

import argparse
import sys
import time
from typing import Dict
import yaml
from bioblend.galaxy import GalaxyInstance


def load_repositories(file_path: str) -> list:
    """Load and parse YAML file containing repositories."""
    with open(file_path) as f:
        data = yaml.safe_load(f)

    repos = data.get('tools', data) if isinstance(data, dict) else data
    if not repos:
        raise ValueError("No repositories found in file")
    return repos


def uninstall_repositories(gi: GalaxyInstance, repos: list,
                          remove_from_disk: bool, delay: float) -> Dict[str, int]:
    """Uninstall all repositories and their revisions."""
    results = {'success': 0, 'failed': 0}

    for repo in repos:
        name = repo.get('name')
        owner = repo.get('owner')
        revisions = repo.get('revisions', [])
        tool_shed = repo.get('tool_shed_url', '')

        if not all([name, owner, revisions, tool_shed]):
            print(f"\n✗ Skipping {name or 'unknown'}: missing required fields")
            results['failed'] += 1
            continue

        if not tool_shed.startswith('http'):
            tool_shed = f'https://{tool_shed}'

        print(f"\n{name} (owner: {owner})")

        for revision in revisions:
            print(f"  Revision: {revision}")
            try:
                gi.toolshed.uninstall_repository_revision(
                    name=name,
                    owner=owner,
                    changeset_revision=revision,
                    tool_shed_url=tool_shed,
                    remove_from_disk=remove_from_disk
                )
                print(f"    ✓ Successfully uninstalled")
                results['success'] += 1
            except Exception as e:
                print(f"    ✗ Failed: {e}")
                results['failed'] += 1

            if delay > 0:
                time.sleep(delay)

    return results


def dry_run(repos: list):
    """Display what would be uninstalled without doing it."""
    print("\n[DRY RUN MODE - No changes will be made]")
    print("=" * 60)
    for repo in repos:
        print(f"\n{repo['name']} (owner: {repo['owner']})")
        print(f"  Tool shed: {repo['tool_shed_url']}")
        for rev in repo.get('revisions', []):
            print(f"  - {rev}")


def print_statistics(repos: list):
    """Print statistics about repositories to be uninstalled."""
    from collections import Counter

    owners = Counter(r.get('owner') for r in repos)
    tool_sheds = Counter(r.get('tool_shed_url') for r in repos)
    total_revisions = sum(len(r.get('revisions', [])) for r in repos)

    print("\nStatistics:")
    print(f"  Total repositories: {len(repos)}")
    print(f"  Total revisions: {total_revisions}")

    print("\n  Repositories by owner:")
    for owner, count in sorted(owners.items(), key=lambda x: x[1], reverse=True):
        print(f"    {owner}: {count}")

    print("\n  Repositories by tool shed:")
    for shed, count in sorted(tool_sheds.items(), key=lambda x: x[1], reverse=True):
        print(f"    {shed}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description='Uninstall repositories from a Galaxy instance using BioBlend',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python uninstall_repos.py https://galaxy.example.org API_KEY repos.yaml
  python uninstall_repos.py https://galaxy.example.org API_KEY repos.yaml --dry-run
  python uninstall_repos.py https://galaxy.example.org API_KEY repos.yaml --keep-on-disk

YAML format:
  tools:
  - name: sra_tools
    owner: iuc
    revisions: [f5ea3ce9b9b0, 8848455c0270]
    tool_shed_url: toolshed.g2.bx.psu.edu

Requirements: pip install bioblend pyyaml
        """
    )

    parser.add_argument('galaxy_url', help='Galaxy instance URL')
    parser.add_argument('api_key', help='Galaxy API key')
    parser.add_argument('repo_file', help='YAML file with repositories to uninstall')
    parser.add_argument('--keep-on-disk', action='store_true',
                       help='Keep repository files on disk')
    parser.add_argument('--delay', type=float, default=5.0,
                       help='Delay between uninstalls in seconds (default: 5.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be uninstalled without doing it')

    args = parser.parse_args()

    # Load repositories
    try:
        repos = load_repositories(args.repo_file)
    except FileNotFoundError:
        print(f"Error: File '{args.repo_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Galaxy URL: {args.galaxy_url}")
    print_statistics(repos)

    if args.dry_run:
        dry_run(repos)
        sys.exit(0)

    print("=" * 60)

    # Connect and uninstall
    try:
        gi = GalaxyInstance(url=args.galaxy_url, key=args.api_key)
        results = uninstall_repositories(gi, repos, not args.keep_on_disk, args.delay)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 60)
    print("Uninstall Summary:")
    print(f"  Successfully uninstalled: {results['success']}")
    print(f"  Failed: {results['failed']}")

    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
