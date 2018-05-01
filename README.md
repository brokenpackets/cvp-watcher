# cvp-watcher
Creates a snapshot, checks compliance on all devices in CVP, and then notifies slack if any devices are out of compliance.
Designed to be run @hourly as a cronjob on CVP. Needs a custom cvprac library for now, but I have a PR in with the cvprac team to merge my functions in.  

Overall flow is:  
1. Check timestamp file for any items older than 1 day  
  1a. delete any that match  
2. Take snapshot  
3. Check Compliance  
  3a. Watch check-compliance sub-events until all show 'COMPLETE' in status.  
4. Collect inventory of all devices, and show compliance status.  
5. for each item not in compliance  
  5a. ignore any that are in current timestamp file.  
  5b. post to slack device fqdn   
  5c. write fqdn to a csv file with a current timestamp.  
