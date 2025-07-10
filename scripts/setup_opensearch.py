#!/usr/bin/env python3
"""
Setup script for creating and configuring Amazon OpenSearch domain for AegisAI
"""
import boto3
import json
import time
import sys
from botocore.exceptions import ClientError

def create_opensearch_domain():
    """Create OpenSearch domain for AegisAI logging"""
    
    # Initialize OpenSearch client
    try:
        opensearch_client = boto3.client('opensearch')
        print("✓ Connected to OpenSearch service")
    except Exception as e:
        print(f"✗ Failed to connect to OpenSearch: {e}")
        sys.exit(1)
    
    domain_name = 'aegis-ai-logs'
    
    # Check if domain already exists
    try:
        response = opensearch_client.describe_domain(DomainName=domain_name)
        print(f"⚠ OpenSearch domain '{domain_name}' already exists")
        
        # Check if domain is active and has endpoint
        domain_status = response['DomainStatus']
        if not domain_status.get('Processing', True) and 'Endpoint' in domain_status:
            domain_endpoint = domain_status['Endpoint']
            print(f"Domain endpoint: https://{domain_endpoint}")
            return domain_endpoint
        else:
            print("Domain exists but is still being created or doesn't have endpoint yet")
            print("Waiting for domain to be ready...")
            
            # Wait for existing domain to be ready
            while True:
                try:
                    status_response = opensearch_client.describe_domain(DomainName=domain_name)
                    processing = status_response['DomainStatus'].get('Processing', True)
                    
                    if not processing and 'Endpoint' in status_response['DomainStatus']:
                        domain_endpoint = status_response['DomainStatus']['Endpoint']
                        print(f"✓ Domain '{domain_name}' is now ready!")
                        print(f"Domain endpoint: https://{domain_endpoint}")
                        return domain_endpoint
                    else:
                        print("Still processing... (this may take several minutes)")
                        time.sleep(60)
                        
                except ClientError as e:
                    print(f"✗ Error checking domain status: {e}")
                    return None
                    
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceNotFoundException':
            print(f"✗ Error checking domain: {e}")
            return None
    
    # Domain configuration
    domain_config = {
        'DomainName': domain_name,
        'EngineVersion': 'OpenSearch_2.3',
        'ClusterConfig': {
            'InstanceType': 't3.small.search',
            'InstanceCount': 1,
            'DedicatedMasterEnabled': False
        },
        'EBSOptions': {
            'EBSEnabled': True,
            'VolumeType': 'gp3',
            'VolumeSize': 20
        },
        'AccessPolicies': json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "*"
                    },
                    "Action": "es:*",
                    "Resource": f"arn:aws:es:*:*:domain/{domain_name}/*"
                }
            ]
        }),
        'DomainEndpointOptions': {
            'EnforceHTTPS': True,
            'TLSSecurityPolicy': 'Policy-Min-TLS-1-2-2019-07'
        },
        'EncryptionAtRestOptions': {
            'Enabled': True
        },
        'NodeToNodeEncryptionOptions': {
            'Enabled': True
        },
        'AdvancedSecurityOptions': {
            'Enabled': True,
            'InternalUserDatabaseEnabled': True,
            'MasterUserOptions': {
                'MasterUserName': 'admin',
                'MasterUserPassword': 'AegisAI@2024!'
            }
        }
    }
    
    try:
        print(f"Creating OpenSearch domain '{domain_name}'...")
        print("⚠ This may take 10-15 minutes to complete...")
        
        response = opensearch_client.create_domain(**domain_config)
        
        print("✓ Domain creation initiated")
        print("Waiting for domain to be active...")
        
        # Wait for domain to be active
        max_wait_time = 30 * 60  # 30 minutes maximum wait time
        start_time = time.time()
        
        while True:
            # Check if we've exceeded maximum wait time
            if time.time() - start_time > max_wait_time:
                print("✗ Timeout waiting for domain to be ready (30 minutes)")
                print("The domain may still be creating. Check AWS console for status.")
                return None
                
            try:
                status_response = opensearch_client.describe_domain(DomainName=domain_name)
                domain_status = status_response['DomainStatus']
                processing = domain_status.get('Processing', True)
                
                if not processing and 'Endpoint' in domain_status:
                    # Check if endpoint is available
                    domain_endpoint = domain_status['Endpoint']
                    print(f"✓ Domain '{domain_name}' is now active!")
                    print(f"Domain endpoint: https://{domain_endpoint}")
                    return domain_endpoint
                elif not processing:
                    print("Domain is active but endpoint not yet available, waiting...")
                    time.sleep(30)
                else:
                    print("Still processing... (this may take several minutes)")
                    time.sleep(60)  # Wait 1 minute before checking again
                    
            except ClientError as e:
                print(f"✗ Error checking domain status: {e}")
                return None
                
    except ClientError as e:
        print(f"✗ Failed to create OpenSearch domain: {e}")
        return None

def create_index_templates(domain_endpoint):
    """Create index templates for structured logging"""
    
    try:
        from opensearchpy import OpenSearch
        
        # Connect to OpenSearch
        client = OpenSearch(
            hosts=[{'host': domain_endpoint, 'port': 443}],
            http_auth=('admin', 'AegisAI@2024!'),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False
        )
        
        print("✓ Connected to OpenSearch domain")
        
    except ImportError:
        print("⚠ opensearch-py not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'opensearch-py'])
        from opensearchpy import OpenSearch
        
        client = OpenSearch(
            hosts=[{'host': domain_endpoint, 'port': 443}],
            http_auth=('admin', 'AegisAI@2024!'),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False
        )
        
    except Exception as e:
        print(f"✗ Failed to connect to OpenSearch: {e}")
        return False
    
    # Index templates
    templates = [
        {
            'name': 'aegis-logs-template',
            'body': {
                'index_patterns': ['aegis-logs-*'],
                'template': {
                    'settings': {
                        'number_of_shards': 1,
                        'number_of_replicas': 0,
                        'index.refresh_interval': '5s'
                    },
                    'mappings': {
                        'properties': {
                            'timestamp': {'type': 'date'},
                            'agent_name': {'type': 'keyword'},
                            'session_id': {'type': 'keyword'},
                            'user_id': {'type': 'keyword'},
                            'activity_type': {'type': 'keyword'},
                            'status': {'type': 'keyword'},
                            'details': {'type': 'object'},
                            'log_level': {'type': 'keyword'},
                            'message': {'type': 'text'}
                        }
                    }
                }
            }
        },
        {
            'name': 'aegis-audit-template',
            'body': {
                'index_patterns': ['aegis-audit-*'],
                'template': {
                    'settings': {
                        'number_of_shards': 1,
                        'number_of_replicas': 0,
                        'index.refresh_interval': '5s'
                    },
                    'mappings': {
                        'properties': {
                            'log_id': {'type': 'keyword'},
                            'timestamp': {'type': 'date'},
                            'session_id': {'type': 'keyword'},
                            'user_context': {'type': 'object'},
                            'event_type': {'type': 'keyword'},
                            'agent_name': {'type': 'keyword'},
                            'activity_details': {'type': 'object'},
                            'input_data': {'type': 'object'},
                            'output_data': {'type': 'object'},
                            'performance_metrics': {'type': 'object'},
                            'compliance_status': {'type': 'keyword'},
                            'risk_level': {'type': 'keyword'},
                            'metadata': {'type': 'object'}
                        }
                    }
                }
            }
        }
    ]
    
    # Create templates
    for template in templates:
        try:
            client.indices.put_index_template(
                name=template['name'],
                body=template['body']
            )
            print(f"✓ Created index template: {template['name']}")
        except Exception as e:
            print(f"✗ Failed to create template {template['name']}: {e}")
    
    # Create initial indices
    initial_indices = [
        f'aegis-logs-{time.strftime("%Y-%m")}',
        f'aegis-audit-{time.strftime("%Y-%m")}'
    ]
    
    for index_name in initial_indices:
        try:
            if not client.indices.exists(index=index_name):
                client.indices.create(index=index_name)
                print(f"✓ Created index: {index_name}")
            else:
                print(f"⚠ Index {index_name} already exists")
        except Exception as e:
            print(f"✗ Failed to create index {index_name}: {e}")
    
    return True

def create_sample_dashboards(domain_endpoint):
    """Create sample dashboards for monitoring"""
    
    try:
        from opensearchpy import OpenSearch
        
        client = OpenSearch(
            hosts=[{'host': domain_endpoint, 'port': 443}],
            http_auth=('admin', 'AegisAI@2024!'),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False
        )
        
        # Sample dashboard configuration
        dashboard_config = {
            'version': '2.3.0',
            'objects': [
                {
                    'id': 'aegis-overview-dashboard',
                    'type': 'dashboard',
                    'attributes': {
                        'title': 'AegisAI Governance Overview',
                        'description': 'Main dashboard for AegisAI governance monitoring',
                        'panelsJSON': json.dumps([
                            {
                                'id': 'agent-activity-panel',
                                'type': 'visualization',
                                'gridData': {'x': 0, 'y': 0, 'w': 24, 'h': 15}
                            }
                        ])
                    }
                }
            ]
        }
        
        # Note: Dashboard creation would require more complex OpenSearch Dashboards API calls
        # This is a placeholder for the structure
        print("✓ Dashboard templates prepared (manual configuration required)")
        
    except Exception as e:
        print(f"⚠ Dashboard setup skipped: {e}")

def main():
    """Main setup function"""
    print("🔍 Setting up OpenSearch domain for AegisAI...")
    print("=" * 50)
    
    # Create OpenSearch domain
    domain_endpoint = create_opensearch_domain()
    
    if domain_endpoint:
        print(f"\n✓ OpenSearch domain created successfully!")
        print(f"Endpoint: https://{domain_endpoint}")
        print(f"Username: admin")
        print(f"Password: AegisAI@2024!")
        
        # Create index templates
        print("\n📋 Creating index templates...")
        if create_index_templates(domain_endpoint):
            print("✓ Index templates created successfully")
        
        # Create sample dashboards
        print("\n📊 Setting up dashboards...")
        create_sample_dashboards(domain_endpoint)
        
        print(f"\n🎉 OpenSearch setup completed!")
        print("\nNext steps:")
        print("1. Update your .env file with the OpenSearch endpoint:")
        print(f"   OPENSEARCH_ENDPOINT={domain_endpoint}")
        print("   OPENSEARCH_USERNAME=admin")
        print("   OPENSEARCH_PASSWORD=AegisAI@2024!")
        print("2. Access OpenSearch Dashboards at:")
        print(f"   https://{domain_endpoint}/_dashboards")
        print("3. Start the backend server with 'python backend/api.py'")
        
    else:
        print("\n✗ OpenSearch setup failed")
        print("Please check your AWS credentials and permissions")

if __name__ == "__main__":
    main()
