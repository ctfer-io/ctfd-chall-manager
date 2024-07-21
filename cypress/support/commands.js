Cypress.Commands.add('login', (username, password) => {
  cy.visit(`${Cypress.env("CTFD_URL")}/login`)
  cy.get('#name').type(username)
  cy.get('#password').type(password)
  cy.get('#_submit').click()
  cy.url().should('contain', 'challenges') 
})


Cypress.Commands.add('create_challenge', (label, scope, mana, mode, mode_value, scenario_path) => {
  cy.visit(`${Cypress.env("CTFD_URL")}/admin/challenges/new`) // go on challenge creation
  cy.wait(500) // wait ctfd
  cy.get(".form-check-label").contains("dynamic_iac").click() // select dynamic_iac
  
  // default attributs
  cy.get("input[placeholder=\"Enter challenge name\"]").type(label)
  cy.get("input[placeholder=\"Enter challenge category\"]").type(label)

  // chall-manager plugins attributs
  cy.get('[data-test-id="scope-selector-id"]').select(scope) // Disabled or Enabled
  cy.get('[data-test-id="mana-create-id"]').type(mana) // set mana cost
  cy.get('[data-test-id="mode-create-id"]').select(mode) // select timeout mode
  if (mode != "none") {
    cy.get('[data-test-id="'+mode+'-create-id"]').type(mode_value) // define timeout seconds
  }
  
  cy.get('[data-test-id="scenario-create-id"]').selectFile(scenario_path) //upload file

  // dynamic attributs
  cy.get("input[placeholder=\"Enter value\"]").type("500")
  cy.get("input[placeholder=\"Enter Decay value\"]").type("10")
  cy.get("input[placeholder=\"Enter minimum value\"]").type("100")

  // Create 
  cy.get(".create-challenge-submit").contains("Create").click()
      
  // Final options
  cy.get("[name=\"flag\"]").type(label)
  cy.get("select[name=\"state\"]").select('Visible')
  
  // Finish creation
  cy.get(".create-challenge-submit").contains("Finish").click()
})

Cypress.Commands.add('popup', (message) => {
  cy.get('.modal-header', { timeout: 20000 }
    ).should('be.visible');
  cy.wait(750)
  cy.get('.modal-footer .btn-primary', { timeout: 20000 }
      ).should('be.visible'
      ).contains(message
      ).click()
  cy.wait(500)
})

Cypress.Commands.add('log_and_go_to_chall', (username, password, challenge_name) => {
  cy.login(username, password)
  cy.visit(`${Cypress.env("CTFD_URL")}/challenges`)
  cy.get("button").contains(challenge_name).click()
  cy.wait(500)
})

Cypress.Commands.add('boot_current_chall', () => {
  // Boot the instance
  cy.get('[data-test-id="cm-button-boot"]').should("be.visible").click()
  // Detect the pop-up, then click on OK
  cy.popup('OK')
})

Cypress.Commands.add('destroy_current_chall', () => {
  cy.get('[data-test-id="cm-button-destroy"]'
  ).should("be.visible"
  ).click()                
  // detect the pop-up, then click on OK
  cy.popup('OK')
})

Cypress.Commands.add('renew_current_chall', () => {

  cy.get('[data-test-id="cm-button-renew"]'
  ).should("be.visible"
  ).click()
  // detect the pop-up, then click OK
  cy.popup('OK')

})

