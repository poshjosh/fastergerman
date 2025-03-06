import { Paths } from './paths'

describe('Index page', () => {
  it('Contains link to game page', () => {
    cy.visit(Paths.baseUrl())
    cy.get("#preposition-trainer").should("exist")
      .click().then(() => {
        cy.url().should('include', Paths.prepositionTrainer)
      })
  })
})