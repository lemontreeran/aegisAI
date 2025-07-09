#!/usr/bin/env python3
"""
Cleanup script for removing AegisAI AWS resources
"""
import boto3
import sys
from botocore.exceptions import ClientError

def cleanup_dynamodb_tables():
    """Delete all AegisAI DynamoDB tables"""
    
    dynamodb = boto3.resource('dynamodb')
    
    table_names = [
        'aegis-policies',
        'aegis-users', 
        'aegis-audit-logs',
        'aegis-feedback',
        'aegis-feedback-analytics'
    ]
    
    deleted_tables = []
    
    for table_name in table_names:
        try:
            table = dynamodb.Table(table_name)
            table.load()
            
            print(f"Deleting table '{table_name}'...")
            table.delete()
            
            print(f"Waiting for table '{table_name}' to be deleted...")
            table.wait_until_not_exists()
            
            print(f"✓ Table '{table_name}' deleted successfully")
            deleted_tables.append(table_name)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"⚠ Table '{table_name}' does not exist")
            else:
                print(f"✗ Failed to delete table '{table_name}': {e}")
    
    return deleted_tables

def cleanup_opensearch_domain():
    """Delete OpenSearch domain"""
    
    opensearch_client = boto3.client('opensearch')
    domain_name = 'aegis-ai-logs'
    
    try:
        print(f"Deleting OpenSearch domain '{domain_name}'...")
        opensearch_client.delete_domain(DomainName=domain_name)
        print(f"✓ Domain '{domain_name}' deletion initiated")
        print("⚠ Domain deletion may take several minutes to complete")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"⚠ Domain '{domain_name}' does not exist")
        else:
            print(f"✗ Failed to delete domain '{domain_name}': {e}")
        return False

def main():
    """Main cleanup function"""
    print("🧹 Cleaning up AegisAI AWS resources...")
    print("=" * 50)
    
    response = input("Are you sure you want to delete all AegisAI resources? (yes/no): ")
    if response.lower() != 'yes':
        print("Cleanup cancelled")
        sys.exit(0)
    
    # Cleanup DynamoDB tables
    print("\n🗄️ Cleaning up DynamoDB tables...")
    deleted_tables = cleanup_dynamodb_tables()
    
    if deleted_tables:
        print(f"✓ Deleted {len(deleted_tables)} DynamoDB tables")
    
    # Cleanup OpenSearch domain
    print("\n🔍 Cleaning up OpenSearch domain...")
    if cleanup_opensearch_domain():
        print("✓ OpenSearch domain deletion initiated")
    
    print("\n🎉 Cleanup completed!")
    print("All AegisAI AWS resources have been removed or scheduled for deletion.")

if __name__ == "__main__":
    main()