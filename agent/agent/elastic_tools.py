"""
LogLens - Elastic Integration
Handles storing and searching audit logs in Elasticsearch.
This replaces reading from a local JSON file with a real search database.
"""

from elasticsearch import Elasticsearch
import json


def connect_to_elastic(cloud_id: str, username: str, password: str) -> Elasticsearch:
    """
    Creates a connection to your Elasticsearch cluster.
    Call this once at the start of the app.
    """
    client = Elasticsearch(
        cloud_id=cloud_id,
        basic_auth=(username, password)
    )
    # Test the connection
    if not client.ping():
        raise ConnectionError("Could not connect to Elasticsearch. Check your credentials.")
    return client


def index_logs(client: Elasticsearch, log_entries: list[dict], index_name: str = "audit-logs") -> int:
    """
    Stores all log entries into Elasticsearch.
    Think of this like uploading your JSON file into a searchable database.
    Returns how many logs were stored.
    """
    # Create the index if it doesn't exist
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name)

    # Upload each log entry one by one
    count = 0
    for i, entry in enumerate(log_entries):
        client.index(
            index=index_name,
            id=str(i),
            document=entry
        )
        count += 1

    # Make sure all documents are searchable immediately
    client.indices.refresh(index=index_name)
    return count


def search_logs(client: Elasticsearch, query: str = None, index_name: str = "audit-logs") -> list[dict]:
    """
    Searches Elasticsearch for audit log entries.
    If query is None, returns ALL logs.
    If query is a string like "203.0.113.45", returns logs matching that.
    """
    if query is None:
        # Get all logs
        response = client.search(
            index=index_name,
            body={"query": {"match_all": {}}, "size": 100}
        )
    else:
        # Search for specific text in any field
        response = client.search(
            index=index_name,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"]  # Search across all fields
                    }
                },
                "size": 100
            }
        )

    # Extract just the log data from Elasticsearch's response format
    hits = response["hits"]["hits"]
    return [hit["_source"] for hit in hits]


def search_by_ip(client: Elasticsearch, ip_address: str, index_name: str = "audit-logs") -> list[dict]:
    """Search logs from a specific IP address."""
    return search_logs(client, query=ip_address, index_name=index_name)


def search_by_user(client: Elasticsearch, email: str, index_name: str = "audit-logs") -> list[dict]:
    """Search logs from a specific user email."""
    return search_logs(client, query=email, index_name=index_name)


def search_errors(client: Elasticsearch, index_name: str = "audit-logs") -> list[dict]:
    """Search for ERROR and ALERT severity logs specifically."""
    response = client.search(
        index=index_name,
        body={
            "query": {
                "terms": {
                    "severity": ["ERROR", "CRITICAL", "ALERT"]
                }
            },
            "size": 100
        }
    )
    hits = response["hits"]["hits"]
    return [hit["_source"] for hit in hits]


def delete_index(client: Elasticsearch, index_name: str = "audit-logs"):
    """Clears all logs from Elasticsearch (useful for resetting between demos)."""
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)