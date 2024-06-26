# ASR-NL-benchmark
## Description
ASR-NL-benchmark is a python package to evaluate and compare the performance of speech-to-text for the Dutch language. Universities and Dutch media companies joined forces to develop this package that makes it easier to compare the performance of various open-source or commercial speech-to-text solutions on Dutch broadcast media. This package wraps around the famous sclite tool (part of [SCTK](https://github.com/usnistgov/SCTK) that has been used for decades in the speech-to-text benchmark evaluations organised by NIST in the US). Further, the package contains several preprocessing files and connectors to databases.

## How to use
### How to: Create a reference file
Reference files can be created using tooling such as:

- [Sourceforge](https://sourceforge.net/projects/transag/files/v2.0.0-b1/)

- [ELAN](https://archive.mpi.nl/tla/elan/download)

<!-- A full annotation protocol can be found [here](https://github.com/opensource-spraakherkenning-nl/ASR-NL-benchmark/issues/7). -->

Please check the guidelines for the reference file in the section below.


### How to: Install
- Install [Docker](https://www.docker.com/products/docker-desktop/)
- Pull the Docker image: <code>docker pull asrnlbenchmark/asr-nl-benchmark</code>

### How to: Run Using the command line only


In order to run the benchmarking tool over a (set of) local hyp and ref file(s) we need docker to mount the local directory where the input files are located. The output files of the benchmarking tool will appear in the same folder. 

The following line runs the benchmarking tool over a local hyp and ref file. Use the absolute file path as the value for the `SOURCE` variable. For `HYPFILENAME` use the filename of the hypfile and for `REFFILENAME` the name of the reffile. 

`HYPFILENAME` and `REFFILENAME` can also be the names of the folders containing the *hypfiles* and *reffiles* respectively. **Make sure** to create a folder named `results` in the `SOURCE` folder before running the command below:

- <code> docker run -it  --mount type=bind,source=SOURCE,target=/input  asrnlbenchmark/asr-nl-benchmark:latest python ASR_NL_benchmark -hyp HYPFILENAME ctm -ref REFFILENAME stm </code>

The results (.dtl, .prf, .spk, and .csv format) can be found inside the `results` folder which can be found in the local `SOURCE` location (see above). 


### How to: Use the Interface

In order to open a User Interface, run a command similar to the one above but now with the optional argument `-interactive`:

- <code> docker run -it -p 5000:5000 --mount type=bind,source=SOURCE,target=/input  asrnlbenchmark/asr-nl-benchmark:latest python ASR_NL_benchmark -interactive </code>

Use a web browser to access the UI by navigating to "http://localhost:5000"

Within the tab "Select folder", enter the path to the hypothesis and reference files:

- Enter the path of the hyp file or the path to a folder containing a set of hyp files: (e.g. "hyp_folder" or "hyp_file.stm")
- Enter the path of the ref file or the path to a folder containing a set of ref files: (e.g. "ref_folder" or "ref_file.stm")
- click "Submit"

A progress bar will appear. As soon as the benchmarking is ready, you will be forwarded to the results. The results (.dtl, .prf, .spk, and .csv format) can be found inside a folder named `results` which can be found on the local `SOURCE` location (see above).

There is a visual bug when forwarding to the results page after benchmarking is complete where the page is blank. To fix it, refresh the page.


### How to: Interpret the results
The final results are saved in .csv format inside a folder named `results` stored locally on the `SOURCE` location (see above). Those results are based upon the .dtl and .spk output files as generated by sclite.

#### The different output files
- .dtl files - Detailed overall report as returned by sclite
- .prf files - Detailed report including string alignments between hypothesis and reference as returned by sclite
- .spk files - Report with scoring for a speaker as returned by sclite
- .csv files - Overall results of the benchmarking as shown in the interface

## Extra arguments
There are extra arguments that you can add to the command line (**NOT** the interface):
- `-skip_hyp_normalization`: Skips the normalization step for the hypothesis file(s) (STILL APPLIES VARIATIONS)
- `-skip_ref_normalization`: Skips the normalization step for the reference file(s) (STILL APPLIES VARIATIONS)

## More about the pipeline
### Normalization
Manual transcripts (used as reference files) sometimes contain abbreviations (e.g. `'n` instead of `een`), symbols (e.g. `&` instead of `en`) and numbers (`4` instead of `vier`). The reference files often contain the written form of the words instead. Since we don't want to penalize the speech-to-text tooling or algorithm for such differences, we normalize both the reference and hypothesis files.

Normalization replacements:

- Symbols:
    - '%' => "procent"
    - '°' => "graden"
    - '&' => "en"
    - '€' => "euro"

- Double spaces:
    - '__' => '_'

- Numbers (e.g.):
    - 4 => "vier"
    - 4.5 => "vier punt vijf"
    - 4,3 => "vier komma drie"

- Combinations (e.g.):
    - 12,3% => 'twaalf komma drie procent'

### Variations
In order to deal with spelling variations, this tool applies a `variations.glm` file to the reference and hypothesis files. This .glm file contains a list of words with their spelling variations and can be found [here](https://github.com/opensource-spraakherkenning-nl/ASR_NL_benchmark/blob/main/ASR_NL_benchmark/variations.glm). Whereas the normalisation step is typically rule-based, the variations are not. Therefore, we invite you all to adjustment to the .glm and to create a pull request with the requested additions.


## Guidelines
### File Naming
In order for the benchmarking tool to match the reference and hypothesis files, both should have exactly the same naming. The only 2 exceptions are:
1. The file extension (.stm for the reference files and .ctm for the hypothesis files)
2. In case you are using subcategories (See Benchmarking subcategories).

### Benchmarking subcategories

example:

Without subcategories:
- program_1.stm
- program_1.ctm
- program_2.stm
- program_2.ctm

With subcategories (sports v.s. news):
- program_1.stm
- program_1-sports.ctm
- program_2.stm
- program_2-news.ctm


### Reference file
The reference file is used as the ground truth. To get the best results, the reference file should meet the following guidelines:

- The reference file should be a Segment Time Mark file (STM), see description below.
- Words should be written according to the modern Dutch spelling
- No abbreviations (e.g. use `bijvoorbeeld` instead of `bv.` or `bijv.` , use `het` instead of `'t`)
- No symbols (use: `procent` instead of `%`)
- No numbers (write out all numbers: `drie` instead of `3`)
- utf-8 encoded

In order to create those reference files, we suggest to use a transcription tool like [transcriber](http://trans.sourceforge.net/en/usermanUS.php).

#### Segment Time Mark (STM)
The Segment Time Mark file, to be used as reference file, consists of a connotation of time marked text segment records. Those segments are separated by a new line and follow the format:

    File_id Channel Speaker_id Begin_Time End_Time <Label> Transcript
  
To comment out a line, start the line with ';;'

##### Example STM
    ;; Some information you want to comment out like a description  
    ;; More information you want to include and comment out  
    ;; like the name of the transcriber, the version or explanation of labels, etc.
    Your_favorite_tv_show_2021_S1_E1 Speaker_01_Female_Native A 0.000 1.527 <o, f1, female> The first line  
    Your_favorite_tv_show_2021_S1_E1 Speaker_01_Female_Native A 1.530 2.127 <o, f1, male> The second text segment  


### Hypothesis file
To get the best results, the hypothesis file (i.e. the output of a speech recognizer) should meet the following guidelines:
- The hypothesis file should be a Time Marked Conversations file (CTM), see the description below.
- utf-8 encoded

#### CTM Format
The Time Marked Conversation file, to be used as hypothesis file, consists of a connotation of time-marked word records. Those records are separated by a new line and follow the format:

    File_id Channel Begin_time Duration Word Confidence

To comment out a line, start the line with ';;'

##### Example CTM

    ;; Some information you want to comment out like a description  
    ;; More information you want to include and comment out  
    Your_favorite_tv_show_2021_S1_E1 A 0.000 0.482 The 0.95  
    Your_favorite_tv_show_2021_S1_E1 A 0.496 0.281 first 0.98  
    Your_favorite_tv_show_2021_S1_E1 A 1.216 0.311 line 0.88  

## Related Documentation
- [sclite documentation](https://github.com/usnistgov/SCTK/blob/master/doc/sclite.htm)
- [Docker how to install on windows](https://docs.docker.com/docker-for-windows/install)
- [Docker how to install on mac](https://docs.docker.com/docker-for-mac/install/)
- [Transcriber documentation & Download](http://trans.sourceforge.net/en/)
