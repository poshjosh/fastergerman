import { Paths } from './paths'

const containsLinkToTrainer = trainer => {
  cy.visit(Paths.baseUrl())
  cy.get(`#${trainer}_trainer`).should("exist")
    .click().then(() => {
    cy.url().should('include', Paths.prepositionTrainer)
  })
}

describe('Index page', () => {
  it('Contains link to preposition trainer', () => {
    containsLinkToTrainer('preposition')
  })
})