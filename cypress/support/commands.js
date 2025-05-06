Cypress.Commands.add('login', (username, password) => {
  cy.visit(`${Cypress.env("CTFD_URL")}/login`)
  cy.get('#name').type(username)
  cy.get('#password').type(password)
  cy.get('#_submit').click()
  cy.url().should('contain', 'challenges') 
})


Cypress.Commands.add('create_challenge', (label, shared, destroy_on_flag, mana, timeout, until, scenario_path, additional, min, max, state) => {
  cy.visit(`${Cypress.env("CTFD_URL")}/admin/challenges/new`) // go on challenge creation
  cy.wait(500) // wait ctfd
  cy.get(".form-check-label").contains("dynamic_iac").click() // select dynamic_iac
  
  // default attributs
  cy.get("input[placeholder=\"Enter challenge name\"]").type(label)
  cy.get("input[placeholder=\"Enter challenge category\"]").type(label)

  // chall-manager plugins attributs
  cy.get('[data-test-id="shared-selector-id"]').select(shared) // Disabled or Enabled
  cy.get('[data-test-id="destroy-on-flag-selector-id"]').select(destroy_on_flag) // Disabled or Enabled
  cy.get('[data-test-id="mana-create-id"]').type(mana) // set mana cost

  if (timeout != ""){
    cy.get('[data-test-id="timeout-create-id"]').type(timeout) // define timeout seconds
  }

  if (until != ""){
    cy.get('[data-test-id="until-create-id"]').type(until) // define until in date
  }

  // dynamic attributs
  cy.get("input[placeholder=\"Enter value\"]").type("500")
  cy.get("input[placeholder=\"Enter Decay value\"]").type("10")
  cy.get("input[placeholder=\"Enter minimum value\"]").type("100")

  cy.get('[data-test-id="scenario-create-id"]').selectFile(scenario_path) //upload file
  cy.wait(1000) // wait file upload 


  // open advanced
  if (additional.length > 0 || min != "0" || max != "0") {
    cy.get('[data-test-id="additional-button-collapse"]').click()
  }

  // Add additional
  if (additional.length > 0){

    additional.forEach((pair, index) => {
      const key = Object.keys(pair)[0];
      const value = pair[key];

      if (index > 0) {
        // Click the add button to add a new row
        cy.get('[data-test-id="additional-button-add"]').click(); // Replace with correct selector
      }

      cy.get("#additional-configuration tbody tr")
        .eq(index)
        .within(() => {
          cy.get('input[placeholder="Key"]').clear().type(key);
          cy.get('input[placeholder="Value"]').clear().type(value);
        });

    });

    cy.get('[data-test-id="additional-button-apply"]').click();
    cy.popup('OK')
  }

  if (min != "0") {
    cy.get('[data-test-id="min-create-id"]').type(min)
  }

  if (max != "0") {
    cy.get('[data-test-id="max-create-id"]').type(max)
  }

  // Create 
  cy.get(".create-challenge-submit").contains("Create").click()
      
  // Final options
  cy.get("[name=\"flag\"]").type(label)
  cy.get("select[name=\"state\"]").select(state)
  
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
  cy.popup('Got it!')
})

Cypress.Commands.add('destroy_current_chall', () => {
  cy.get('[data-test-id="cm-button-destroy"]'
  ).should("be.visible"
  ).click()                
  // detect the pop-up, then click on OK
  cy.popup('Got it!')
})

Cypress.Commands.add('renew_current_chall', () => {

  cy.get('[data-test-id="cm-button-renew"]'
  ).should("be.visible"
  ).click()
  // detect the pop-up, then click OK
  cy.popup('Got it!')

})

