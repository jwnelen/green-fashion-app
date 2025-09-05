output "mysql_instance_name" {
  description = "MySQL instance name"
  value       = google_sql_database_instance.mysql_instance.name
}

output "mysql_instance_ip" {
  description = "MySQL instance IP address"
  value       = google_sql_database_instance.mysql_instance.public_ip_address
}

output "mysql_database_name" {
  description = "MySQL database name"
  value       = google_sql_database.mysql_database.name
}

output "mysql_connection_secret_id" {
  description = "Secret Manager secret ID for MySQL connection string"
  value       = google_secret_manager_secret.mysql_connection_string.secret_id
}
