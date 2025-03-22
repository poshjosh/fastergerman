# How to setup a custom website for an AWS Elastic Beanstalk environment

Buy domain (e.g. `mysite.com`) from DNS Provider e.g. GoDaddy.

Create an AWS Route 53 Hosted Zone for `mysite.com`.

Change the nameservers in the DNS Provider (e.g. GoDaddy) to AWS Route 53 `NS Record`s.

Request for an SSL Certificate on AWS Certificate Manager from the same region you created 
the AWS Route 53 Hosted Zone. 

- For FQDN use both `mysite.com` and  `*.mysite.com`

- Select DNS Validation for the certificate.

- The certificate will be pending validation until you create a Route 53 record from AWS 
Certificate Manager.

- The option to create the necessary Route 53 records will be presented to you.

Wait till the certificate status is `issued`.

Go to AWS Elastic Beanstalk.

- In load balancer add an HTTPS listener for port 443 and use the default process (of port 80) 
as target.

Go to AWS Route 53

- Create an A record to the AWS elastic beanstalk environment.

Original nameservers for fastergerman on GoDaddy

- ns57.domaincontrol.com
- ns58.domaincontrol.com

