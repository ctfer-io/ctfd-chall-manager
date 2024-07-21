describe("Permform tests for CTFd in the User Land", () => {
    // We assume that CTFd, the Plugins and CM are correctly installed to work together before continue.
    // We assume that the challenge actions are already tested before.
    // The next tests will used existing challenges that has been created in previous tests.

    // We assume that requirements is configured before :
    // With admin account, set CTFd to be on user_mode = users if not
    // With admin account, create 3 users
    // With admin account, create 2 teams 
    // With the first and second user, join the first team
    // With the third user, join the second team

    beforeEach(() => {
        // Delete all instances if exists
        cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
        cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/instances`)
        cy.wait(500)
        cy.get('[data-test-id="cm-checkbox-all"]').click()
        cy.wait(500)
        cy.get('[data-test-id="cm-button-destroy"]').click()
        cy.popup('Yes')
        cy.wait(5000)
      })

    it('I only can control my instance and I can t get infos from the others', () => {
        let connectionInfoUser1
        let connectionInfoUser2
        let connectionInfoUser3
        // Test 1 : I only can control my instance 
        //          And I can't get infos from the others
        
        // With the first user, deploy one instance        
        cy.log_and_go_to_chall("user1", "user1", "cypress-timeout") 
        cy.boot_current_chall() // try to boot
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }
            ).should("be.visible"
            ).then($user1 => {
                connectionInfoUser1 = $user1.text();
            })
        
        // With the second user, check that I retrieve the information of the first user
        cy.log_and_go_to_chall("user2", "user2", "cypress-timeout") 
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }
        ).should("be.visible"
        ).then($user2 => {
            connectionInfoUser2 = $user2.text();

            expect(connectionInfoUser1).to.equal(connectionInfoUser2);
        })      
        
        // With the third user, detect that we can't see the instance of the first teams
        cy.log_and_go_to_chall("user3", "user3", "cypress-timeout") 
        cy.boot_current_chall() // try to boot
        // retrieve connectionInfo for the current user, then compare with the previous
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }
        ).should("be.visible"
        ).then($user3 => {
            connectionInfoUser3 = $user3.text();
            expect(connectionInfoUser1).not.to.equal(connectionInfoUser3);
            expect(connectionInfoUser2).not.to.equal(connectionInfoUser3);
        })  

        // With the third user, renew the instance, check that the until is reset
        cy.log_and_go_to_chall("user3", "user3", "cypress-timeout") 
        let beforeUntilUser
        let currentUntilUser

        cy.get('[data-test-id="cm-challenge-count-down"]', { timeout: 20000 }
        ).should("be.visible"
        ).then($user3 => {
            beforeUntilUser = $user3.text();
        }) 
        cy.wait(2000)
        cy.renew_current_chall()

        cy.get('[data-test-id="cm-challenge-count-down"]', { timeout: 20000 }
        ).should("be.visible"
        ).then($user3 => {
            currentUntilUser = $user3.text();
            expect(currentUntilUser).not.to.equal(beforeUntilUser);
        }) 

        // With the third user, destroy the instance, check that the instance is destroy
        cy.log_and_go_to_chall("user3", "user3", "cypress-timeout") 
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }
        ).should("be.visible")
        cy.destroy_current_chall()
        cy.get('[data-test-id="cm-button-boot"]', { timeout: 20000 }
        ).should("be.visible")

    })

    
    it("I can't deploy instance of challenge if my mana is too low", () => {
        // Test 2 : I can't deploy instance of challenge if my mana is too low

        // With the first user, deploy an instance that cost 5
        cy.log_and_go_to_chall("user1", "user1", "cypress-until") 
        cy.boot_current_chall()
        cy.get('[data-test-id="cm-connectionInfo-id"]').should("be.visible")


        // With the first user, try to deploy a second one
        cy.log_and_go_to_chall("user1", "user1", "cypress-none") 
        cy.boot_current_chall()
        cy.get('[data-test-id="cm-connectionInfo-id"]').should("be.visible")

        // With the first user, detect (the denial pop-up or that connectionInfo does not exists)
        cy.log_and_go_to_chall("user1", "user1", "cypress-timeout") 
        cy.boot_current_chall() // try to boot
        // detect the pop-up, then click on OK
        //cy.popup('OK')
        cy.get('[data-test-id="cm-connectionInfo-id"]').should("not.be.visible")

        // With the first user, destroy the first instance
        cy.log_and_go_to_chall("user1", "user1", "cypress-until") 
        cy.destroy_current_chall()
        

        // Try again, and detect the connectionInfo generated, if exists it's good.
        cy.log_and_go_to_chall("user1", "user1", "cypress-timeout") 
        cy.boot_current_chall() 
        cy.get('[data-test-id="cm-connectionInfo-id"]').should("be.visible")
    })

    
    // Test 5: My mana is given back when my instance is expired
    // With the first user, deploy one instance
    // Destroy the instance on CM via DELETE request (janitor is not present)
    // With the first user, check that my instance is no longer here and my mana is recover

    it("I have the same connectionInfo for challenge in scope global and (as user) I can't manipulate the instance.", () => {
        // Test 3 : I have the same connectionInfo for challenge in scope global 
        //          And I can't manipulate the instance.
        
        // With the admin account, deploy an instance of challenge with scope global
        cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
        cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/panel`)
        cy.wait(500)

        cy.get('[data-test-id="panel-source-pattern"]')
        .clear().type("0") // source=0 for global
  
        // select the last challenges 
        cy.get('[type="checkbox"]').last().check() // FIXME this is a workaround to get the last (cypress-global-enable in challenge.cy.js)
        cy.get('[data-test-id="panel-preprovisioning-button"]').click()
        cy.popup('Yes')
        cy.wait(2500)

        let connectionInfoUser1
        let connectionInfoUser2
        let connectionInfoUser3

        // With the first user, check that I can't use my buttons (wallah tqt c'est aussi bloqué en API :pouet: )
        cy.log_and_go_to_chall("user1", "user1", "cypress-global-enable") 
        cy.get('[data-test-id="cm-button-boot"]').should("not.exist")
        cy.get('[data-test-id="cm-button-renew"]').should("not.exist")
        cy.get('[data-test-id="cm-button-restart"]').should("not.exist")
        cy.get('[data-test-id="cm-button-destroy"]').should("not.exist")


        cy.log_and_go_to_chall("user1", "user1", "cypress-global-enable") 
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }
        ).should("be.visible"
        ).then($user1 => {
            connectionInfoUser1 = $user1.text();
        })

        // With the second user, detect the connectionInfo, check that I have the same
        cy.log_and_go_to_chall("user2", "user2", "cypress-global-enable") 
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }
        ).should("be.visible"
        ).then($user2 => {
            connectionInfoUser2 = $user2.text();
            expect(connectionInfoUser1).to.equal(connectionInfoUser2);
        })

        // With the third user, detect the connectionInfo, check that I have the same
        cy.log_and_go_to_chall("user3", "user3", "cypress-global-enable") 
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }
        ).should("be.visible"
        ).then($user3 => {
            connectionInfoUser3 = $user3.text();
            expect(connectionInfoUser2).to.equal(connectionInfoUser3);
        })

        
    })   

    it("I can't submit a flag from another instance", () => {
        // With the first user, deploy one instance
        cy.log_and_go_to_chall("user1", "user1", "cypress-none")
        // Boot the instance
        cy.boot_current_chall()    
    
        /// With the third user, deploy one instance
        cy.log_and_go_to_chall("user3", "user3", "cypress-none")
        // Boot the instance
        cy.boot_current_chall()    
    
        // With admin account, get the flags on the 2 instances
        let flagUser1;
        let flagUser3;
        cy.login(Cypress.env('CTFD_NAME'), Cypress.env('CTFD_PASSWORD'))
        cy.visit(`${Cypress.env("CTFD_URL")}/plugins/ctfd-chall-manager/admin/instances`)
        cy.wait(500)
    
        // Find the index of the "Flag" column
        cy.get('thead tr th').each(($el, index) => {
        if ($el.text().trim() === 'Flag') {
            cy.wrap(index).as('flagColumnIndex');
        }
        });
    
        // Retrieve the flag for the first user (source-id="1")
        cy.get('@flagColumnIndex').then(flagColumnIndex => {
        cy.get('input[data-source-id="1"]').closest('tr').within(() => { // FIXME sourceId == 1 is maybe not Team1
            cy.get('td').eq(flagColumnIndex).invoke('text').then(text => {
            flagUser1 = text.trim();
            });
        });
        });
    
        // Retrieve the flag for the second user (source-id="2")
        cy.get('@flagColumnIndex').then(flagColumnIndex => {
        cy.get('input[data-source-id="2"]').closest('tr').within(() => { // FIXME sourceId == 2 is maybe not Team2
            cy.get('td').eq(flagColumnIndex).invoke('text').then(text => { 
            flagUser3 = text.trim();
            expect(flagUser3).not.to.equal(flagUser1);
            });
        });
        });
    
        // Ensure that flagUser3 is set before trying to use it
        cy.get('@flagColumnIndex').then(() => {
        // Log in as the first user and try to submit the flag of the second team
        cy.log_and_go_to_chall("user1", "user1", "cypress-none") 
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }).should('be.visible');
        
        // Ensure flagUser3 is defined before typing it
        cy.wrap(flagUser3).should('not.be.undefined').then(flag => {
            cy.get('input[placeholder="Flag"]').type(flag, { parseSpecialCharSequences: false });
            cy.get('button').contains('Submit').click();
            cy.get('#result-message').should('be.visible').contains("Incorrect");
        });
        });
    
        // Ensure that flagUser3 is set before trying to use it
        cy.get('@flagColumnIndex').then(() => {
        // Log in as the third user and try to submit the flag of the second team
        cy.log_and_go_to_chall("user3", "user3", "cypress-none") 
        cy.get('[data-test-id="cm-connectionInfo-id"]', { timeout: 20000 }).should('be.visible');
        
        // Ensure flagUser3 is defined before typing it
        cy.wrap(flagUser3).should('not.be.undefined').then(flag => {
            cy.get('input[placeholder="Flag"]').type(flag, { parseSpecialCharSequences: false });
            cy.get('button').contains('Submit').click();
            cy.get('#result-message').should('be.visible').contains("Correct");
        });
        });
    });
    
    it("I can provide the flag of CTFd as fallback", () => {
        // With the first user, deploy one instance
        cy.log_and_go_to_chall("user3", "user3", "cypress-until")
        // Boot the instance
        cy.boot_current_chall()    
               
        // Type the fallback flag         
        cy.get('input[placeholder="Flag"]').type("cypress-until", { parseSpecialCharSequences: false });
        cy.get('button').contains('Submit').click();
        cy.get('#result-message').should('be.visible').contains("Correct");

    });

    it("I cant provide a flag if instance is not booted", () => {
        // With the first user, deploy one instance
        cy.log_and_go_to_chall("user3", "user3", "cypress-global-enable")
                    
        // Type the fallback flag         
        cy.get('input[placeholder="Flag"]').type("POUET", { parseSpecialCharSequences: false });
        cy.get('button').contains('Submit').click();
        cy.get('#result-message').should('be.visible').contains("Expired");

    });

    

})
