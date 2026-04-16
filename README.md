# Goose

The Warwick Cybersecurity Society's Official Discord Bot.

## Functionality

Goose currently offers three commands to manage events in the society server:

- `create_event`
- `edit_event` (event_id: int)
- `cancel_event` (event_id: int)

They handle events across Discord (both Scheduled Events and Event Announcements) and Google Calendar.

## Running

### Environment Variables

A `./goose/.env` file shall be created with the envars required by the bot. Please contact me (@VulcanShot) if you need this file.

### Credentials

Since we are using Google as our calendar provider (and as an improvised DBMS, to be honest), we have generated a [service account](/google_credentials.json) to use the API. Please contact me if you need valid credentials. Avoid creating new service accounts for testing purposes.

### Docker

TODO