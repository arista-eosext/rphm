### On an EOS device
```
EOS#copy scp://username@10.10.10.1/src/triggertrap/rpmbuild/triggertrap-0.1.0-1.rpm extension:
Password:
triggertrap-0.1.0-1.rpm                       100%   17KB  17.0KB/s   00:00    
Copy completed successfully.
EOS#show extensions 
Name                                       Version/Release           Status RPMs
------------------------------------------ ------------------------- ------ ----
triggertrap-0.1.0-1.rpm                    0.1.0/1                   A, NI     1

A: available | NA: not available | I: installed | NI: not installed | F: forced
EOS#extension triggertrap-0.1.0-1.rpm
EOS#show extensions
Name                                       Version/Release           Status RPMs
------------------------------------------ ------------------------- ------ ----
triggertrap-0.1.0-1.rpm                    0.1.0/1                   A, I      1

A: available | NA: not available | I: installed | NI: not installed | F: forced
vEOS-1#
```

### On a linux system
    rpm -Uvh rpmbuild/triggertrap-0.1.0-1.rpm

OR

    pip install -e <path-to-this-dir>
