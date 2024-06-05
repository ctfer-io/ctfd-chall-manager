describe('Dynamic IaC Challenge', () => {

    beforeEach(() => {
      cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
    })


    it('Test all buttons for Users', () => {
      let label = generateRandomString(10)
      cy.create_challenge(label, "1", "Recreate", "timeout", "300", Cypress.env('SCENARIO_PATH'))
      cy.wait(5000) // wait ctfd to create challenge and redirect to edit sections
      cy.visit(`${Cypress.env("CTFD_URL")}/challenges`)
      cy.get("button").contains(label).click()

      // launch instance 
      cy.get('[data-test-id="cm-button-boot"]').click()


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
