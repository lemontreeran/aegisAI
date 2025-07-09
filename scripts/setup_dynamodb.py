#!/usr/bin/env python3
"""
Setup script for creating required DynamoDB tables for AegisAI
"""
import boto3
import json
import sys
from botocore.exceptions import ClientError

def create_dynamodb_tables():
    """Create all required DynamoDB tables for AegisAI"""
    
    # Initialize DynamoDB client
    try:
        dynamodb = boto3.resource('dynamodb')
        print("✓ Connected to DynamoDB")
    except Exception as e:
        print(f"✗ Failed to connect to DynamoDB: {e}")
        sys.exit(1)
    
    # Table definitions
    tables = [
        {
            'TableName': 'aegis-policies',
            'KeySchema': [
                {'AttributeName': 'policy_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'policy_id', 'AttributeType': 'S'},
                {'AttributeName': 'policy_name', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'policy-name-index',
                    'KeySchema': [
                        {'AttributeName': 'policy_name', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'aegis-users',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'username', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'username-index',
                    'KeySchema': [
                        {'AttributeName': 'username', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'aegis-audit-logs',
            'KeySchema': [
                {'AttributeName': 'log_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'log_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'timestamp', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'user-index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'aegis-feedback',
            'KeySchema': [
                {'AttributeName': 'feedback_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'feedback_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'category', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'timestamp', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'category-index',
                    'KeySchema': [
                        {'AttributeName': 'category', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'aegis-feedback-analytics',
            'KeySchema': [
                {'AttributeName': 'analytics_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'analytics_id', 'AttributeType': 'S'},
                {'AttributeName': 'date', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'date-index',
                    'KeySchema': [
                        {'AttributeName': 'date', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    # Create tables
    created_tables = []
    for table_config in tables:
        table_name = table_config['TableName']
        
        try:
            # Check if table already exists
            existing_table = dynamodb.Table(table_name)
            existing_table.load()
            print(f"⚠ Table '{table_name}' already exists, skipping...")
            continue
            
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                print(f"✗ Error checking table '{table_name}': {e}")
                continue
        
        try:
            # Create table
            print(f"Creating table '{table_name}'...")
            table = dynamodb.create_table(**table_config)
            
            # Wait for table to be created
            print(f"Waiting for table '{table_name}' to be active...")
            table.wait_until_exists()
            
            print(f"✓ Table '{table_name}' created successfully")
            created_tables.append(table_name)
            
        except ClientError as e:
            print(f"✗ Failed to create table '{table_name}': {e}")
    
    return created_tables

def populate_sample_data():
    """Populate tables with sample data for testing"""
    
    dynamodb = boto3.resource('dynamodb')
    
    # Sample policies
    policies_table = dynamodb.Table('aegis-policies')
    sample_policies = [
        {
            'policy_id': 'policy_001',
            'policy_name': 'Content Safety Policy',
            'policy_type': 'content_filter',
            'status': 'active',
            'applicable_roles': ['admin', 'analyst', 'user'],
            'applicable_activities': ['prompt_submission', 'output_generation'],
            'rules': [
                {
                    'type': 'content_filter',
                    'name': 'Harmful Content Filter',
                    'blocked_terms': ['violence', 'hate', 'discrimination'],
                    'enforcement_actions': ['warn', 'block']
                }
            ],
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        },
        {
            'policy_id': 'policy_002',
            'policy_name': 'Privacy Protection Policy',
            'policy_type': 'privacy',
            'status': 'active',
            'applicable_roles': ['admin', 'analyst', 'user'],
            'applicable_activities': ['all'],
            'rules': [
                {
                    'type': 'content_filter',
                    'name': 'PII Detection',
                    'blocked_terms': ['ssn', 'social security', 'credit card'],
                    'enforcement_actions': ['block', 'escalate']
                }
            ],
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        },
        {
            'policy_id': 'policy_003',
            'policy_name': 'Role-Based Access Control',
            'policy_type': 'access_control',
            'status': 'active',
            'applicable_roles': ['user'],
            'applicable_activities': ['admin_functions'],
            'rules': [
                {
                    'type': 'role_restriction',
                    'name': 'Admin Function Restriction',
                    'allowed_roles': ['admin'],
                    'restricted_activities': ['policy_management', 'user_management'],
                    'enforcement_actions': ['block']
                }
            ],
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
    ]
    
    try:
        for policy in sample_policies:
            policies_table.put_item(Item=policy)
        print(f"✓ Added {len(sample_policies)} sample policies")
    except Exception as e:
        print(f"⚠ Failed to add sample policies: {e}")
    
    # Sample users
    users_table = dynamodb.Table('aegis-users')
    sample_users = [
        {
            'user_id': 'demo_admin',
            'username': 'demo_admin',
            'role': 'admin',
            'permissions': ['read', 'write', 'admin', 'audit', 'policy_manage'],
            'created_at': '2024-01-01T00:00:00Z',
            'last_login': '2024-01-07T00:00:00Z',
            'status': 'active'
        },
        {
            'user_id': 'demo_analyst',
            'username': 'demo_analyst',
            'role': 'analyst',
            'permissions': ['read', 'write', 'audit'],
            'created_at': '2024-01-01T00:00:00Z',
            'last_login': '2024-01-07T00:00:00Z',
            'status': 'active'
        },
        {
            'user_id': 'demo_user',
            'username': 'demo_user',
            'role': 'user',
            'permissions': ['read'],
            'created_at': '2024-01-01T00:00:00Z',
            'last_login': '2024-01-07T00:00:00Z',
            'status': 'active'
        }
    ]
    
    try:
        for user in sample_users:
            users_table.put_item(Item=user)
        print(f"✓ Added {len(sample_users)} sample users")
    except Exception as e:
        print(f"⚠ Failed to add sample users: {e}")

def main():
    """Main setup function"""
    print("🚀 Setting up DynamoDB tables for AegisAI...")
    print("=" * 50)
    
    # Create tables
    created_tables = create_dynamodb_tables()
    
    if created_tables:
        print(f"\n✓ Successfully created {len(created_tables)} tables:")
        for table in created_tables:
            print(f"  - {table}")
        
        # Populate sample data
        print("\n📊 Populating sample data...")
        populate_sample_data()
    else:
        print("\n⚠ No new tables were created")
    
    print("\n🎉 DynamoDB setup completed!")
    print("\nNext steps:")
    print("1. Configure your AWS credentials if not already done")
    print("2. Run 'python scripts/setup_opensearch.py' to set up OpenSearch")
    print("3. Start the backend server with 'python backend/api.py'")

if __name__ == "__main__":
    main()
