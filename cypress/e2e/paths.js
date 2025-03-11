import { Env } from "./env";

export const Paths = {
  prepositionTrainer: '/trainers/preposition',
  baseUrl: function() {
    return Cypress.env(Env.baseUrl)
  },
  url: function (path) {
    return Paths.baseUrl() + path
  }
}