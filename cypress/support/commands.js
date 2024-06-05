// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

Cypress.Commands.add('login', (username, password) => {
    cy.visit(`${Cypress.env("CTFD_URL")}/login`)
    cy.get('#name').type(username)
    cy.get('#password').type(password)
    cy.get('#_submit').click()
    cy.url().should('contain', 'challenges') 
  })


Cypress.Commands.add('create_challenge', (label, mana, updateStrategy, mode, mode_value, scenario_path) => {
    cy.visit(`${Cypress.env("CTFD_URL")}/admin/challenges/new`) // go on challenge creation
    cy.wait(500) // wait ctfd
    cy.get(".form-check-label").contains("dynamic_iac").click() // select dynamic_iac

    // default attributs
    cy.get("input[placeholder=\"Enter challenge name\"]").type(label)
    cy.get("input[placeholder=\"Enter challenge category\"]").type(label)

    // chall-manager plugins attributs
    cy.get('[data-test-id="mana-create-id"]').type(mana) // set mana cost
    cy.get('[data-test-id="updateStrategy-create-id"]').select(updateStrategy) // set updatestarted to Restart
    cy.get('[data-test-id="mode-create-id"]').select(mode) // select timeout mode
    cy.get('[data-test-id="timeout-create-id"]').type(mode_value) // define timeout seconds
    cy.get('[data-test-id="scenario-create-id"]').selectFile(scenario_path) //upload file

    // dynamic attributs
    cy.get("input[placeholder=\"Enter value\"]").type("500")
    cy.get("input[placeholder=\"Enter Decay value\"]").type("10")
    cy.get("input[placeholder=\"Enter minimum value\"]").type("100")

    // Create 
    cy.get(".create-challenge-submit").contains("Create").click()
    cy.wait(7500)

    // Final options
    cy.get("[name=\"flag\"]").type(label)
    cy.get("select[name=\"state\"]").select('Visible')
    
    // Finish creation
    cy.get(".create-challenge-submit").contains("Finish").click()
  })