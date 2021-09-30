# There can only be a single job definition per file.
# Create a job with ID and Name 'example'
job "strongdm-gw-test" {
  datacenters = ["datacenter"]
  type        = "service"

  meta {
    owner = "testing@example.com"
  }

  constraint {
    attribute = meta.storage
    value     = "local"
    operator  = "=="
  }
  vault {
    policies      = ["YOUR_VAULT_POLICY"]
    env           = true
    change_mode   = "signal"
    change_signal = "SIGHUP"
  }

  group "strongdm-gateway-group" {
    count = 1

    restart {
      interval = "1h"
      attempts = 240
      delay    = "15s"
      mode     = "delay"
    }

    network {
      mode = "bridge"

      port "strongdm_proxy" {
        static = "5000"
        to     = "5000"
      }
    }

    task "strongdm_gateway" {
      driver = "docker"

      config {

        image = "quay.io/sdmrepo/relay:latest"
        ports = ["strongdm_proxy"]

        logging {
          type = "json-file"
        }
      }
      template {

        data = <<EOD
SDM_RELAY_TOKEN={{ with secret "VAULT_PATH_TO/strongdm/gateways/GATEWAY_NAME" }}{{ .Data.SDM_RELAY_TOKEN}}{{ end}}
EOD

        destination = "secrets/file.env"
        env         = true
      }


      resources {
        cpu    = 4000
        memory = 4096
      }

      service {
        name = "strongdm-gw" # GATEWAY_NAME
        tags = [
          "traefik.enable=true",
          "traefik.tags=tcp",
          "traefik.protocol=tcp",
          "traefik.frontend.rule=Host:GATEWAY_NAME.example.com"
        ]

        port = "strongdm_proxy"
        check {
          type     = "tcp"
          interval = "10s"
          port     = "strongdm_proxy"
          timeout  = "2s"
        }
      }
    }
  }
}
