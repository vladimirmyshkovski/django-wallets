# -- FILE: features/example.feature
Feature: Create 1 tariff, 1 membership and bring it to completion

	Scenario: we create two users, the first user sends the crypto currency to the second, then the second user checks his balance
		Given 2 users
		When the first user send to coins to second user
		Then the second user checks his address, and his balance is greater than 0