describe('Verify that admin pages is available', () => {

  beforeEach(() => {
    cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
  })

  it('Admin available', () => {
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/settings`)
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/instances`)
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/mana`)
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/panel`)
  })

  it('Configure CM', () => {
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/settings`)
    cy.get('[data-test-id="chall-manager:chall-manager_api_url"]')
      .clear()
      .type(Cypress.env("PLUGIN_SETTINGS_CM_API_URL"))
    
    cy.get('[data-test-id="chall-manager:chall-manager_mana_total"]')
      .clear()
      .type(Cypress.env("PLUGIN_SETTINGS_CM_MANA_TOTAL"))

    cy.get('[data-test-id="plugin-settings-submit"]').click()
  }) 
})