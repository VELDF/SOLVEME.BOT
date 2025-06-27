import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-historico',
  imports: [CommonModule],
  templateUrl: './historico.component.html',
  styleUrl: './historico.component.css'
})
export class HistoricoComponent {
  historico = [
    { titulo: 'Como configurar o VPN', data: 'Hoje', hora: '9:41 AM' },
    { titulo: 'Como resetar o MFA', data: 'Ontem', hora: '2:15 PM' },
    { titulo: 'Como executar o mapeamento de pasta', data: 'Segunda-feira', hora: '10:02 AM' },
    { titulo: 'Assistência com as configurações', data: 'Segunda-feira', hora: '9:32 PM' },
  ];

    voltar() {
      window.history.back();
  
  }
}