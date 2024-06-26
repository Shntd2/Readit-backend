# Projects development sequence

## Use `models.py` file to manage direct interactions with the database

* Preliminarily provide connection to PostgreSQL server using SQLAlchemy
    * Classes here (Models) will represent database tables
    * Every column of that database tables will have its variable
* Add actual values to `SQLALCHEMY_DATABASE_URI = 'postgresql:///data.db'` variable of `DevelopmentConfig`
  and `ProductionConfig` classes from `config.py` file
    * Add the actual URI of new database
* Presumably create two databases:
    * PostgreSQL database where will be stored users data for login (sign in, sign out, change password if forgotten)
      logic
    * NoSQL (maybe MongoDB) database for storing in certain order summaries of uploaded PDFs chunks
    * After sending last summary of uploaded PDF file that summaries chain must be automatically deleted from database

## Use `main_page.py` file as a welcome page. It will contain

1. Description of the app
    * What is it for
    * What are its benefits
    * It is very important to convey information to the user that messages with summaries will be sent to email address
      which will be mentioned in registration
2. Feedback section
    * Here users will be able to send comments and suggestions about the project
3. Login page
    * This page is crucial because without login user won't be able to use the app
    * It is very important to convey information to the user that messages with summaries will be sent to users email
      address which will be mentioned in registration
    * Implement sign in and sign up logic in `login.py` file
        * Add function to `login.py` that will handle users sessions and setting cookies
            * Find a way not to store sensitive and session data in apps environment
            * Think about AWS S3 bucket
        * `login.py` must be connected directly to `models.py`
            * To check for existing users username/email and password in the database for login
            * To add new users username, email and password for sign up
            * So here must be two classes: sign in (for existing users) and sign up (for new users)
                * First opens sign in page
                * In sign in page must be button redirecting to sign up page
            * Create client-side and server-side data validation system in sign in and in sign up logic
            * If user chooses direct registration without connecting to existing Google account:
                * He will need to enter his:
                * Name (variable)
                    * Forbid signs usage besides the hyphen
                    * Add length limit
                * Username (variable)
                    * Implement checking for value repetitions
                    * Mention what signs are forbidden to use in username
                    * Add length limit
                * Password (variable)
                    * Add min length limit
                * Re-enter password
                    * Implement logic of matching two entered password values
                    * If they're mismatched, output that info correctly in frontend
                * Create account button
                    * It will redirect user to page with info about next registration step: email verification
                    * After sign up he should end registration process by opening special link which app will send to a
                      users email mentioned in registration
                    * Link will provide user to sign in page where he will enter his username and password
        * Add ability to login via Google account
            * Use [Google’s oAuth API](https://support.google.com/googleapi/answer/6158849?hl=en) for that perpose. It
              enables external apps to use Google’s authentication system to manage their user login
    * Implement password recovery logic in sign in page
        * Here user will enter his email by which he was registered
        * Then login page in connection with `models.py` will look for that email in registered users table from
          database
            * If there's match
                * it will send link to that email which will redirect to form where user will enter new password and
                  re-enter password
                * Add min length limit
                * Implement logic of matching two entered password values
                * If they're mismatched, output that info correctly in frontend
            * If entered email is not in registered users table
                * Output message in front that user with such email is not registered in the application

## Create `personal_page.py` file as personal page of the user

* Here frontend must contain active subscriptions list
* And Create new subscription button which should redirect to `routes.py` - page where user can upload its PDF file
    * Implement new file uploading page (front) in `routes.py` file upload.html file is index.html now
    * After creating users session, its email address from `models.py` must be used in backend. So it is needed to
      connect `personal_page.py` with `models.py` and assign users email received from users database to
      variable `recipient`
* Then uploaded PDF file will process to `pdf_summary.py`
* `pdf_summary.py` will cut PDF to JSON chunks and send them to `ai_summarizer.py`
    * Move `send_summary_via_email(summary_chunks, recipient)` function from `pdf_summary.py` to `ai_summarizer.py`
    * After that in `send_summary_via_email` function specify `recipient` variable which consists of users email from
      users database (via `models.py`)
    * Add to `pdf_summary.py` function that will send all chunks of uploaded PDF to `ai_summarizer` for further
      processing
* `ai_summarizer.py` will create summary based on every JSON chunk of uploaded PDF, where every JSON chunk will be
  provided with universal prompt to make summary of provided part of PDF
    * `ai_summarizer.py` should generate summaries to all chunks of uploaded PDF and store them separately preliminarily
      in NoSQL database
    * Summaries must be connected to each other in chronological order and tagged by the uploaded PDF file name, unique
      id and username
* `ai_summarizer.py` will send summaries of one PDF file in chronological order to `email_service.py`
    * This addon should be implemented in `send_summary_via_email` function
* `email_service.py` will send summaries to recipient as `ai_summarizer.py` will provide them. It means
  that `ai_summarizer.py` will send summaries to `email_service.py` according to the schedule. `email_service.py`
  functionality will be simple: it gets message from `ai_summarizer.py` and sends it to recipient - one by one

## Modify `pdf_summary.py`

* Unify JSON chunks formatting to make them easy for the reader to perceive
    * Try to use Unstructured.io for that task
    * Make it ignore non-relevant data: annotations, tables of contents, gratitude's and etc.
        * Think about keywords usage, but also search for other methods
    * In `pdf_summary.py` in this line must be located recipients
      email `status_code, response_message = send_summary_via_email(summary_chunks, 'recipients@mail.com')`. Implement
      here `recipient` variable with usernames email from users database

## Modify `routes.py`

* The `allowed_file` function only checks the file extension. Implement additional validation to ensure uploaded files
  are actually the intended file types and not malicious files
* `upload_file` function defines path where uploaded PDF files get stored. Change it to the server path, now it is local
  path `file_path = os.path.join(DevelopmentConfig.UPLOAD_FOLDER, secure_filename(file.filename))`

## Additional API's integration

* [Abstract Email Validation](https://www.abstractapi.com/api/email-verification-validation-api) - validates email
  addresses for deliverability and spam
* Presumably [Warrant](https://warrant.dev/) - APIs for authorization and access control. Use as a backup option, better
  create it by yourself

## Mailing Integration

* Set up an email service provider (e.g., Gmail, SendGrid) for sending emails programmatically
* Configure SMTP settings in web application to enable email sending - DONE
* Create email templates for sending abbreviated chapters - DONE
* Configure email sending by schedule
    * Implement a scheduler (e.g. cron job, Celery) to send emails daily

## Intermediate testing

* Test the web application thoroughly, including file uploads, text summarization, email sending, and scheduled tasks
* Perform both functional and usability testing to ensure a smooth user experience

## Deploy web application to a hosting platform

* Buy a domain name
* Choose a hosting provider for deploying web application (e.g. AWS, Heroku, DigitalOcean)
* Configure the deployment environment and deploy application

## Monitoring and Maintenance

* Implement logging and monitoring solutions to track application performance and errors

## Tasks to solve in perspective

* Think about active subscription limitations for every user for not to take up too much space on server
* Think how to effectively adapt web application to different screen sizes and devices

## Users tests

* Organize for few users test of application in different stages of development