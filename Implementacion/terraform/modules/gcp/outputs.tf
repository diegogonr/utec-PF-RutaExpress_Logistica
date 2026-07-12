output "bq_dataset_id" { value = google_bigquery_dataset.tracking.dataset_id }
output "bq_table_id" { value = google_bigquery_table.tracking_projection.table_id }
output "cloud_run_uri" { value = google_cloud_run_v2_service.projector.uri }
output "projector_service_account" { value = google_service_account.projector.email }
