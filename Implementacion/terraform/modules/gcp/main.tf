terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.40"
    }
  }
}

resource "google_bigquery_dataset" "tracking" {
  dataset_id                 = var.bq_dataset_id
  friendly_name              = "RutaExpress MVP tracking projection"
  description                = "Proyección CQRS — lectura E8"
  location                   = var.region
  delete_contents_on_destroy = true
  labels                     = var.labels
}

resource "google_bigquery_table" "tracking_projection" {
  dataset_id = google_bigquery_dataset.tracking.dataset_id
  table_id   = "tracking_projection"

  schema = jsonencode([
    { name = "order_id", type = "STRING", mode = "REQUIRED" },
    { name = "status", type = "STRING", mode = "NULLABLE" },
    { name = "last_event", type = "STRING", mode = "NULLABLE" },
    { name = "updated_at", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "correlation_id", type = "STRING", mode = "NULLABLE" }
  ])

  labels = var.labels
}

resource "google_service_account" "projector" {
  account_id   = "${var.prefix}-projector"
  display_name = "Cloud Run CQRS projector"
}

resource "google_project_iam_member" "projector_bq" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.projector.email}"
}

resource "google_cloud_run_v2_service" "projector" {
  name     = var.cloud_run_service
  location = var.region
  labels   = var.labels

  template {
    service_account = google_service_account.projector.email

    containers {
      image = var.projector_image

      env {
        name  = "BQ_DATASET"
        value = google_bigquery_dataset.tracking.dataset_id
      }
      env {
        name  = "BQ_TABLE"
        value = google_bigquery_table.tracking_projection.table_id
      }
      env {
        name  = "EVENTHUB_CONNECTION_SECRET"
        value = "projects/${var.project_id}/secrets/${var.eventhub_secret_id}"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }

  depends_on = [google_project_iam_member.projector_bq]
}

resource "google_secret_manager_secret" "eventhub_bridge" {
  secret_id = "${var.prefix}-eventhub-conn"
  labels    = var.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "eventhub_bridge" {
  count       = var.eventhub_connection_string != "" ? 1 : 0
  secret      = google_secret_manager_secret.eventhub_bridge.id
  secret_data = var.eventhub_connection_string
}

resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_v2_service.projector.location
  service  = google_cloud_run_v2_service.projector.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
