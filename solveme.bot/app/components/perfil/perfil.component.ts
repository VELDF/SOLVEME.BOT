import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-perfil',
  standalone: true, // ✅ obrigatório para Standalone Components
  imports: [CommonModule, FormsModule], // ✅ aqui importa o FormsModule
  templateUrl: './perfil.component.html',
  styleUrls: ['./perfil.component.css']
})
export class PerfilComponent {
  telefone = '(61)9 00000000';
  senha = '********';
  isSenhaVisivel = false;

  toggleSenha() {
    this.isSenhaVisivel = !this.isSenhaVisivel;
  }

  salvar() {
    console.log('Dados salvos');
  }

  alterarSenha() {
    console.log('Alterar senha');
  }

  voltar() {
    window.history.back();
}
}
