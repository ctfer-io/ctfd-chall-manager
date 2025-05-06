describe('Dynamic IaC Challenge', () => {

  beforeEach(() => {
    cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
  })

  it('Create challenges before testing it in UserLand', () => {
    // create a timeout challenge
    cy.create_challenge("cypress-timeout", "Disabled", "Disabled", "5","6000", "", Cypress.env('SCENARIO_PATH'), [], "0", "0", "Visible")
    // create a until challenge
    cy.create_challenge("cypress-until", "Disabled", "Disabled",  "5", "", "2222-01-20T11:00", Cypress.env('SCENARIO_PATH'), [], "0", "0", "Visible")
    // create a timeout challenge
    cy.create_challenge("cypress-combine", "Disabled", "Disabled", "5","6000", "2222-01-20T11:00", Cypress.env('SCENARIO_PATH'),[], "0", "0", "Visible")
    // create a none challenge
    cy.create_challenge("cypress-none", "Disabled", "Disabled", "5","", "", Cypress.env('SCENARIO_PATH'), [], "0", "0", "Visible")
    // create a destroy on flag challenge
    cy.create_challenge("cypress-destroy-on-flag", "Disabled", "Enabled", "5","", "", Cypress.env('SCENARIO_PATH'), [], "0", "0", "Visible")

    cy.create_challenge("cypress-additional", "Disabled", "Disabled", "5","", "", Cypress.env('SCENARIO_PATH'), [{"a": "b"}, {"c": "d"}], "0", "0", "Visible")

    cy.create_challenge("cypress-pooler", "Disabled", "Disabled", "5","", "", Cypress.env('SCENARIO_PATH'), [], "1", "2", "Visible")

    // create a shared instance (this one must be the last)
    cy.create_challenge("cypress-shared-enable", "Enabled", "Disabled", "5","", "", Cypress.env('SCENARIO_PATH'), [], "0", "0", "Visible")

  })

  it('pre-provisionnning of 1 challenges for 6 peoples', () => {
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/panel`)
    cy.get('[data-test-id="panel-source-pattern"]')
      .clear()
      .type("1,5,19-22")

      // select the last challenges 
      cy.get('[type="checkbox"]').last().check()

      cy.get('[data-test-id="panel-provisioning-button"]').click()

      cy.contains('Yes').click()

  })

})
