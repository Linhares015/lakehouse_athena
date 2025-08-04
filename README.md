# Lakehouse Athena
docker run -e "ACCEPT_EULA=Y" \
  -e "SA_PASSWORD=MyStrongPassword@123" \
  -p 1433:1433 \
  --name sqlserver_sp \
  -d mcr.microsoft.com/mssql/server:2022-latest


sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER


docker compose up airflow-init
docker compose up
