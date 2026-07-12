output "ecs_cluster_name" { value = aws_ecs_cluster.main.name }
output "mobile_alb_dns" { value = aws_lb.mobile.dns_name }
output "dynamodb_table_name" { value = aws_dynamodb_table.mobile_outbox.name }
output "s3_evidence_bucket" { value = aws_s3_bucket.evidence.bucket }
output "sqs_mobile_queue_url" { value = aws_sqs_queue.mobile_bridge.url }
output "event_bus_name" { value = aws_cloudwatch_event_bus.bridge.name }
output "kms_key_arn" { value = aws_kms_key.evidence.arn }
