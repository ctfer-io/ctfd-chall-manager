describe('Dynamic IaC Challenge', () => {

    beforeEach(() => {
      cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
    })

    let label = generateRandomString(10)

    it('Test all buttons for Users', () => {
      
      cy.create_challenge(label, "1", "Recreate", "timeout", "300", Cypress.env('SCENARIO_PATH'))
      cy.wait(5000) // wait ctfd to create challenge and redirect to edit sections
      cy.visit(`${Cypress.env("CTFD_URL")}/challenges`)
      cy.get("button").contains(label).click()

      // launch instance 
      cy.get('[data-test-id="cm-button-boot"]').click()
      // TODO:
      // detect the confirmation pop-up and the timeout

      // renew the instance 
      // detect the confirmation pop-up and the timeout reseted

      // delete the instance
      // detect the confirmation pop-up and check instance is not deployed anymore
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

  function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}
