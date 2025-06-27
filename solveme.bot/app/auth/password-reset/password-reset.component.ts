import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-password-reset',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.css'] 
})
export class PasswordResetComponent {
  step = 1;

  email = '';
  code = '';
  newPassword = '';
  confirmPassword = '';

  enviarCodigo() {
    console.log('Enviar código para:', this.email);
    this.step = 2;
  }

  validarCodigo() {
    console.log('Código digitado:', this.code);
    this.step = 3;
  }

  alterarSenha() {
    if (this.newPassword !== this.confirmPassword) {
      alert('As senhas não coincidem');
      return;
    }

    console.log('Nova senha:', this.newPassword);
    this.step = 4;
  }

  voltar(): void {
  window.location.href = '/login';
}
}
