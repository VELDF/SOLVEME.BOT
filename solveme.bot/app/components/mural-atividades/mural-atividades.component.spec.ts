import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MuralAtividadesComponent } from './mural-atividades.component';

describe('MuralAtividadesComponent', () => {
  let component: MuralAtividadesComponent;
  let fixture: ComponentFixture<MuralAtividadesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MuralAtividadesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MuralAtividadesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
