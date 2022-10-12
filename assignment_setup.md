# Home assignments (Jiri Hruban)

## 1, Object store path min/max analysis [Problem solving]
You have a specific prefix + key structure in your objects store (can be S3, HDFS, ...), that looks like this:
`protocol://bucket/base_path/specific_path/keys`  and a key has a structure of `id=some_value/month=yyyy-MM-dd/object{1, 2, 3, ...}`

Example:
s3://my-bucket/xxx/yyy/zzz/abc/id=123/month=2019-01-01/2019-01-19T10:31:18.818Z.gz
s3://my-bucket/xxx/yyy/zzz/abc/id=123/month=2019-02-01/2019-02-19T10:32:18.818Z.gz
s3://my-bucket/xxx/yyy/zzz/abc/id=333/month=2019-03-01/2019-06-19T10:33:18.818Z.gz
s3://my-bucket/xxx/yyy/zzz/def/id=123/month=2019-10-01/2019-10-19T10:34:18.818Z.gz
s3://my-bucket/xxx/yyy/zzz/def/id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz

You have a function `get_all_keys(bucket, full_path) -> Iterator[str]` for getting all the keys for a full path (base_path + specific_path).

Notes:
On the input you know your bucket, base_path and all the specific paths you want to generate output for.
Also as shown in the example the month subkey has format of a date, but it's always yyyy-MM-01, so effectively it only gives you information about the year and month. Objects (files) within this structure have a timestamp, but this is a timestamp of when they have been created. For illustration, the last line in the example is an object (file) that was generated at '2019-12-19T10:35:18.818Z', but data in it are for the id of '333' and month of 2019-11.

**For each specific_path (there can be many):**
 - A, calculate for each id a minimum and maximum month (there cannot be gaps between moths)
 - B, write the output to a json file
 - C, (optional/bonus) there can be gaps between months (missing months), so report them also in some appropriate structure

### 2, Serving an ML model as an HTTP endpoint [Practical skill]
This task is about creating an application that sets up several HTTP endpoints with a well thought through structure. 

#### Endpoint 1
Imagine that you would like to serve newly trained sentiment analysis model via HTTP endpoint. The endpoint should accept requests with following structure:
```json
{
    "text": <str>,
    "languageCode": <str>
}

```
for example:
```json
{
    "text": "This task is awesome. Nope, just kidding.",
    "languageCode": "en"
}
```
and should respond with following response structure:
```json
{
    "sentiment": <"neutral" | "negative" | "positive">
}
```
A real model's output would obviously take into account what the input data is, but let's keep it simple and respond with a randomly chosen sentiment among the 3 choices stated above. 

#### Endpoint 2
Clients also want to provide feedback for incorrect prediction, which could be then used during retraining phase. To solve this create a third endpoint that would store incoming requests for further use, for simplicity we suggest storing it as files on the local file system. The request will be in following structure:
```json
{
    "text": "This task is awesome. Nope, just kidding.",
    "languageCode": "en",
    "sentiment": "negative",
    "isGoodTranslation": <true | false>
}
```
If this feedback is already stored, do not store it again. Think about how you would make your solution robust and maintainable (validation, logging, unit tests,…).
You can use any language (Python/Java/Scala) and any framework that you are comfortable with (Flask/FastAPI/Spring Boot/...).