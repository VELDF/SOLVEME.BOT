import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MuralAtividadesAdminComponent } from './mural-atividades-admin.component';

describe('MuralAtividadesAdminComponent', () => {
  let component: MuralAtividadesAdminComponent;
  let fixture: ComponentFixture<MuralAtividadesAdminComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MuralAtividadesAdminComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MuralAtividadesAdminComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
