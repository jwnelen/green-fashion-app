# Secret Manager for MongoDB configuration
# Reference existing MongoDB URI secret
data "google_secret_manager_secret" "mongodb_uri" {
  secret_id = "${var.service_name}-${var.environment}-mongodb-uri"
}

data "google_secret_manager_secret_version" "mongodb_uri" {
  secret = data.google_secret_manager_secret.mongodb_uri.id
}
