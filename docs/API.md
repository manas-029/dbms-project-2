# API Documentation

Base URL: `http://localhost:5000/api`

## Authentication

### POST `/auth/login`
Body:
```json
{"email":"spoorthi123@gmail.com","password":"Password1"}
```
Response:
```json
{"token":"JWT_TOKEN","user":{"id":1,"name":"Spoorthi","email":"spoorthi123@gmail.com","role":"user"}}
```

Send protected requests with:
`Authorization: Bearer JWT_TOKEN`

## User

### GET `/me`
Returns the authenticated user's id, name, email, and role.

## Platforms

### GET `/platforms`
Returns all connected platforms for the current user.

### POST `/platforms`
```json
{
  "name": "Example App",
  "category": "Productivity",
  "dataCollected": "Email, contacts",
  "permissions": "Contacts access",
  "thirdPartyAccess": true,
  "privacySetting": "Weak",
  "retentionMonths": 30,
  "breachFound": false
}
```

## Consents

### GET `/consents`
Returns consent history with platform, permission, purpose, status, and sharing partner.

## Risks

### GET `/risks`
Calculates and returns latest score, level, factors, and recommendation.

## Alerts

### GET `/alerts`
Returns notification alerts for high exposure, retention issues, consent expiry, and breaches.

## Analytics

### GET `/analytics`
Returns monthly exposure score, risk score, consent count, and platform count.

## Deletion Requests

### GET `/deletion-requests`
Returns deletion request status records.

### POST `/deletion-requests`
```json
{
  "platformName": "OldForum",
  "dataType": "Posts and username",
  "reason": "I no longer use this service"
}
```

## Admin

### GET `/admin/audit-logs`
Requires an admin JWT. Returns audit trail rows with timestamp, user, action, entity, and IP address.
