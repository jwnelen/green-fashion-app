# MySQL Cloud SQL Instance
resource "google_sql_database_instance" "mysql_instance" {
  name             = "${var.service_name}-mysql-${var.environment}"
  database_version = "MYSQL_8_0"
  region           = var.region

  settings {
    tier              = var.db_tier
    edition          = "ENTERPRISE"
    disk_size        = var.db_disk_size
    disk_type        = "PD_SSD"
    availability_type = var.high_availability ? "REGIONAL" : "ZONAL"

    backup_configuration {
      enabled                        = true
      start_time                    = "03:00"
      location                      = var.region
      binary_log_enabled            = true
      transaction_log_retention_days = 7
    }

    ip_configuration {
      ipv4_enabled    = true
      private_network = null
      authorized_networks {
        value = "0.0.0.0/0"
        name  = "Allow all"
      }
    }

    maintenance_window {
      day          = 1
      hour         = 4
      update_track = "stable"
    }

    user_labels = var.labels
  }

  deletion_protection = var.deletion_protection
}

# MySQL Database
resource "google_sql_database" "mysql_database" {
  name     = "green-fashion-db"
  instance = google_sql_database_instance.mysql_instance.name
}

# MySQL User
resource "google_sql_user" "mysql_user" {
  name     = "dbUser"
  instance = google_sql_database_instance.mysql_instance.name
  password = var.db_password
}

# Store MySQL connection details in Secret Manager
resource "google_secret_manager_secret" "mysql_connection_string" {
  secret_id = "${var.service_name}-mysql-connection-${var.environment}"

  labels = var.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "mysql_connection_string" {
  secret = google_secret_manager_secret.mysql_connection_string.id
  secret_data = "mysql://${google_sql_user.mysql_user.name}:${google_sql_user.mysql_user.password}@${google_sql_database_instance.mysql_instance.public_ip_address}:3306/${google_sql_database.mysql_database.name}"
}
