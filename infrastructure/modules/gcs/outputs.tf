output "bucket_name" {
  description = "Name of the GCS bucket for images"
  value       = google_storage_bucket.images_bucket.name
}

output "bucket_url" {
  description = "URL of the GCS bucket"
  value       = google_storage_bucket.images_bucket.url
}
