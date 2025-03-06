import { Env } from "./env";

export const Paths = {
  prepositionTrainer: '/preposition-trainer',
  baseUrl: function() {
    return Cypress.env(Env.baseUrl)
  },
  url: function (path) {
    return Paths.baseUrl() + path
  }
}