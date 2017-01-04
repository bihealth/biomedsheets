.. _faq:

==========================
Frequently Asked Questions
==========================

---------
Why JSON?
---------

While YAML is easier to process by human beings, JSON has better tool support and is used more widely.
In particular, JSON schema is widely accepted as are JSON pointers, and RDBMS such as Postgres have good support for JSON fields as well.

Further, JSON is valid YAML, so YAML parsers can be used for reading the JSON files and the resulting structures can then be validated by JSON validators.
