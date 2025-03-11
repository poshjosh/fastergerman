// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
import { Paths } from "../e2e/paths"

Cypress.Commands.add('hasTextIgnoreSpace', selector => {
  cy.get(selector).invoke("text").then(text => {
    if (!text?.trim()) {
      throw new Error("Expected some text, but got '" + text + "'")
    }
  })
})
Cypress.Commands.add('hasNoTextIgnoreSpace', selector => {
  cy.get(selector).invoke("text").then(text => {
    if (text?.trim()) {
      throw new Error("Expected no text, but got '" + text + "'")
    }
  })
})
Cypress.Commands.add('updateSettings', settings => {
  cy.visit(Paths.url(Paths.prepositionTrainer))
  cy.get("#settings_tab").should("exist").click().then(() => {
    for (let key in settings) {
      const val = settings[key]
      if (typeof val === "boolean") {
        cy.get(`[name="${key}"][value="${val}"]`).should("exist").check()
      } else {
        cy.get(`[name="${key}"]`).should("exist").clear().type(settings[key])
      }
    }
    cy.get("#save_game_as").should("exist").type("TestGame_" + Date.now().toString())
    cy.get("#action_update").should("exist").click().then(() => {
      cy.get("#page_error").invoke("text").then(text => {
        if (text) {
          throw new Error("Should not have error. But found: " + text)
        }
      })
      for (let key in settings) {
        const val = settings[key]
        if (typeof val === "boolean") {
          cy.get(`[name="${key}"][value="${val}"]`).should("be.checked")
        } else {
          cy.get(`[name="${key}"]`).should("have.value", val)
        }
      }
    })
  })
})