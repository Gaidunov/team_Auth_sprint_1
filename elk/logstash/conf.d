input {
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  if "auth_app" in [tags] {
    mutate { add_field => { "index" => "auth_app-%{+YYYY.MM.dd}" } }
  }
  else if "fast_api_app" in [tags] {
    mutate { add_field => { "index" => "fast_api_app-%{+YYYY.MM.dd}" } }
  }
  else {
    mutate { add_field => { "index" => "other-%{+YYYY.MM.dd}" } }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[index]}"
  }
}