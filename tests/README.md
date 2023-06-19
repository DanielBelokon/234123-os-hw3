# Credits

Tests were created and tested by Almog Tabo and Nadav Tur.



# Instructions:

Extract the tests folder to where your server files are, so that you have a test folder where your server file is.

Make sure you run make in your server directory, so that public/ folder and it's all content are there.

Make sure you have pip installed, otherwise look https://pip.pypa.io/en/stable/installation/

run the following commands:

```
cd tests
pip3 install -r requirements.txt
python3 -m pytest -n auto
```

The last line will ensure you run the test in parallel according to your cpu count.

In order to run a single test file you can run

```
python3 -m pytest -n auto <name_of_file.py>
```

In order to run a single test function you can run

```
python3 -m pytest -n auto <name_of_file.py> -k "<name_of_function>"
```

Example:

```
python3 -m pytest test_segel.py -k "test_stats_dispatch"
```



# FAQ

Q: I see I failed a test, and it says something about expected and got. What do I do?

A: we test your outputs (headers, content) using regex. Use this website: https://regex101.com/ (or any other regex tester) to see where the matching failed. Insert the "expected" string as the regular expression and the "got" string as the test string.
What I like about this website is that they have a "regex debugger" which can help you find exactly where it failed the matching.

Q: I see an exception related to ConnectionError or something like that, what does it mean?

A: Your server probably dropped a connection that it shouldn't. We recommend checking the test name and parameters, it should give you a hint on what to look for. 

Q: What is the meaning of "tests_segel"?
A: The course staff published last semester a description of the tests they used on the student's code. We tried to replicate it. See tests_segel_description.txt