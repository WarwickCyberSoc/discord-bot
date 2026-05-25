# Goose

The Warwick Cybersecurity Society's Official Discord Bot.

## Functionality

Goose currently offers three commands to manage events in the society server:

- `create_event`
- `edit_event` (event_id: int)
- `cancel_event` (event_id: int)

They handle events across Discord (both Scheduled Events and Event Announcements) and Google Calendar. Permissions for access to the commands should be set on the Server Settings rather than programatically to provide a better UX.

## Running

### Environment Variables

For development, `./goose/.env` is used. Please contact me (@VulcanShot) if you need this file. For Docker, the envars are pulled from `prod.env` and injected directly to the container.

- `GUILD` (development only): Server ID, used to facilitate development without having to wait for Discord to acknowledge changes in the bot
- `EVENTS_CHANNEL`: Channel ID where the bot should send event announcements
- `CALENDAR_ID`: Calendar ID, using Google Calendar at the moment
- `PUBLICITY_ROLE`: Role ID for the Publicity (formerly known as Marketing) Officer Role, used to ping them to request images for events
- `BOT_TOKEN`: Discord Bot Token (found on Discord Developer Portal and Vaultwarden)

### Credentials

Since we are using Google as our calendar provider (and as an improvised DBMS, to be honest), we have generated a [service account](/google_credentials.json) to use the API. Please contact me if you need valid credentials. Avoid creating new service accounts for testing purposes.

It is not included directly in the image, but as a read-only volume.
