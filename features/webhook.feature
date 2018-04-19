# -- FILE: features/webhook.feature
Feature: Checking the transfer of crypto currency between users with the set and removal of Webhook.

  Scenario: we create two users, the first user sends the crypto currency to the second, then the second user checks his balance
    Given 2 unique users
     When the first user send to coins to second user and set webhook
     Then the second user checks his address, and his balance is greater than 0
     Then remove webhook