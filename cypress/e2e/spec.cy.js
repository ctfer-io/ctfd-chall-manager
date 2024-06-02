describe('Verify that admin pages is available', () => {

  beforeEach(() => {
    cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
  })

  it('passes', () => {
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/settings`)
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/instances`)
    cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/mana`)
  })
})