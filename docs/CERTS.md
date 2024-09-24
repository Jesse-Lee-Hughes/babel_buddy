## Renewal of Certificates

Currently the certificate is mounted to the docker container instead of being generated within the nginx container. 


```sudo certbot --nginx -d babelbuddy.com.au -d www.babelbuddy.com.au --email jessesaddress@gmail.com --non-interactive --agree-tos```

There are a few options for improving this. I can either make the certs auto-renew within the container, or have
the NGINX server running on the VM. 


