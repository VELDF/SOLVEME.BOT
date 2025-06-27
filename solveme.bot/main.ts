// C:\solveme.bot\front-chatbot\src\main.ts

import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config'; // Importa a configuração global da aplicação
import { AppComponent } from './app/app.component'; // Importa o componente raiz da sua aplicação

// Inicia a aplicação Angular, associando o componente raiz (AppComponent)
// com a configuração global (appConfig)
bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err)); // Captura e loga quaisquer erros que ocorram durante o bootstrap