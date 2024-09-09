describe('Dynamic IaC Challenge', () => {

  beforeEach(() => {
    cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
  })

  it('Create challenges before testing it in UserLand', () => {
    // create a timeout challenge
    cy.create_challenge("cypress-timeout", "Disabled", "5","6000", "", Cypress.env('SCENARIO_PATH'), "Visible")
    // create a until challenge
    cy.create_challenge("cypress-until", "Disabled", "5", "", "2222-01-20T11:00", Cypress.env('SCENARIO_PATH'), "Visible")
    // create a timeout challenge
    cy.create_challenge("cypress-combine", "Disabled", "5","6000", "2222-01-20T11:00", Cypress.env('SCENARIO_PATH'), "Visible")
    // create a none challenge
    cy.create_challenge("cypress-none", "Disabled", "5","", "", Cypress.env('SCENARIO_PATH'), "Visible")
    // create a global scope
    cy.create_challenge("cypress-global-enable", "Enabled", "5","", "", Cypress.env('SCENARIO_PATH'), "Visible")
  })

  it('pre-provisionnning of 1 challenges for 6 peoples', () => {
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/panel`)
    cy.get('[data-test-id="panel-source-pattern"]')
      .clear()
      .type("1,5,19-22")

      // select the last challenges 
      cy.get('[type="checkbox"]').last().check()

      cy.get('[data-test-id="panel-preprovisioning-button"]').click()

      cy.contains('Yes').click()

  })

})
