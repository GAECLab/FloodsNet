Following instructions from here: https://github.com/nasaharvest/cropharvest/blob/main/release_steps.md

Get a Zenodo token: log on to Zenodo, go to username, click the dropdown,
select Applications -> New Token  
Name: global_flood_training  
Token: YourToken

    cd global_flood_training/data
[for me: cd /Users/mtulbure/Documents/projects/InProgress/global_flood_training/data]  
```
tar -czf open_source_training.tar.gz open_source_training
```

    export ZENODO_TOKEN=<your zenodo token>

[for me: export ZENODO_TOKEN=<>   
gives the following error:
zsh: parse error near `\n'

but this works:

    export ZENODO_TOKEN=YourToken

Go to the newest version of FloodsNet on Zenodo and click "New Version" and leave the page open  
Q: do I first need to upload manually, correct? I believe yes.  
[Every time I want to upload a new version I go through these moves and get a new deposition id]

Copy the deposit id from URL (after /deposit/) ie. https://zenodo.org/deposit/7574427 and set it as an environment variable:  
`export DEPOSITION_ID=7574427`

Copied the zenodo_upload.sh from [here](https://github.com/nasaharvest/cropharvest/blob/main/zenodo_upload.sh).

    chmod 755 zenodo_upload.sh

Run:
`./zenodo_upload.sh $DEPOSITION_ID /Users/mtulbure/Documents/projects/InProgress/global_flood_training/data/trial.tar copy.gz`

`./zenodo_upload-experimenting.sh $DEPOSITION_ID /Users/mtulbure/Documents/projects/InProgress/global_flood_training/floodsnet/test.txt` looks like its working but file isnt uploaded

 `bash zenodo_upload.sh $DEPOSITION_ID test.txt ` this worked!

 The reason why files were not uploading was because they were empty and thus 0 in size and Zenodo, without 
 complaining was not uploading them