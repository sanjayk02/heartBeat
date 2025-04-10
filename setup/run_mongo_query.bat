@echo off
wsl bash -c "mongosh -u admin -p MSvauy7s --authenticationDatabase admin --eval 'use heartBeat; db.activity_pulse.find()'"
pause
